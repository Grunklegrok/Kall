'use client';

import { useEffect, useId, useRef, useState } from 'react';

const GOOGLE_CSE_ID = '551e53ca5b28b4060';
const SCRIPT_ID = 'kall-google-cse-script';

type SearchElement = {
  execute: (query: string) => void;
  clearAllResults?: () => void;
};

type GoogleCseApi = {
  render: (config: {
    div: HTMLElement;
    tag: 'searchresults-only';
    gname: string;
    attributes: Record<string, string | boolean>;
  }) => void;
  getElement: (gname: string) => SearchElement | null;
};

declare global {
  interface Window {
    __gcse?: { parsetags: 'explicit' };
    google?: { search?: { cse?: { element?: GoogleCseApi } } };
    __kallGoogleCsePromise?: Promise<void>;
  }
}

function loadGoogleCse() {
  if (window.google?.search?.cse?.element) return Promise.resolve();
  if (window.__kallGoogleCsePromise) return window.__kallGoogleCsePromise;

  window.__gcse = { parsetags: 'explicit' };
  window.__kallGoogleCsePromise = new Promise<void>((resolve, reject) => {
    const existing = document.getElementById(SCRIPT_ID) as HTMLScriptElement | null;
    const finish = () => {
      let attempts = 0;
      const waitForApi = window.setInterval(() => {
        attempts += 1;
        if (window.google?.search?.cse?.element) {
          window.clearInterval(waitForApi);
          resolve();
        } else if (attempts > 100) {
          window.clearInterval(waitForApi);
          reject(new Error('Google job search did not finish loading.'));
        }
      }, 50);
    };

    if (existing) {
      finish();
      return;
    }

    const script = document.createElement('script');
    script.id = SCRIPT_ID;
    script.async = true;
    script.src = `https://cse.google.com/cse.js?cx=${GOOGLE_CSE_ID}`;
    script.onload = finish;
    script.onerror = () => reject(new Error('Google job search could not be loaded.'));
    document.head.appendChild(script);
  });

  return window.__kallGoogleCsePromise;
}

export default function GoogleJobSearchResults({ query }: { query: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const reactId = useId().replace(/:/g, '');
  const elementName = `kall-job-results-${reactId}`;
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    if (!query || !containerRef.current) return;

    async function renderResults() {
      try {
        await loadGoogleCse();
        if (cancelled || !containerRef.current) return;

        containerRef.current.replaceChildren();
        const api = window.google?.search?.cse?.element;
        if (!api) throw new Error('Google job search is unavailable.');

        api.render({
          div: containerRef.current,
          tag: 'searchresults-only',
          gname: elementName,
          attributes: {
            autoSearchOnLoad: false,
            linkTarget: '_blank',
            enableImageSearch: false,
          },
        });

        const element = api.getElement(elementName);
        if (!element) throw new Error('Google job results could not be initialized.');
        element.execute(query);
        setError('');
      } catch (caught) {
        if (!cancelled) setError(caught instanceof Error ? caught.message : 'Unable to display job results.');
      }
    }

    void renderResults();
    return () => { cancelled = true; };
  }, [elementName, query]);

  return (
    <div className="google-job-search" aria-live="polite">
      {error && <p className="notice">{error}</p>}
      <div ref={containerRef} className="google-job-search-results" />
    </div>
  );
}
