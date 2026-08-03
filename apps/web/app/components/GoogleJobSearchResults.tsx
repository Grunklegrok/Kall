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

function decorateResults(container: HTMLElement, profileId?: string) {
  container.querySelectorAll<HTMLElement>('.gsc-webResult.gsc-result').forEach((result) => {
    if (result.dataset.kallActions === 'true') return;
    const titleLink = result.querySelector<HTMLAnchorElement>('.gs-title a');
    if (!titleLink?.href) return;

    result.dataset.kallActions = 'true';
    const title = titleLink.textContent?.trim() || 'Imported job opportunity';
    const snippet = result.querySelector<HTMLElement>('.gs-snippet')?.textContent?.trim() || '';

    const actions = document.createElement('div');
    actions.className = 'kall-search-result-actions';

    const apply = document.createElement('a');
    apply.className = 'button kall-result-apply';
    apply.textContent = 'Apply with Kall';
    const params = new URLSearchParams({
      external_url: titleLink.href,
      title,
      snippet,
    });
    if (profileId) params.set('profile', profileId);
    apply.href = `/apply?${params.toString()}`;

    const view = document.createElement('a');
    view.className = 'button secondary';
    view.textContent = 'View posting';
    view.href = titleLink.href;
    view.target = '_blank';
    view.rel = 'noreferrer';

    actions.append(apply, view);
    result.appendChild(actions);
  });
}

export default function GoogleJobSearchResults({ query, profileId }: { query: string; profileId?: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const reactId = useId().replace(/:/g, '');
  const elementName = `kall-job-results-${reactId}`;
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    let observer: MutationObserver | null = null;
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

        observer = new MutationObserver(() => {
          if (containerRef.current) decorateResults(containerRef.current, profileId);
        });
        observer.observe(containerRef.current, { childList: true, subtree: true });

        const element = api.getElement(elementName);
        if (!element) throw new Error('Google job results could not be initialized.');
        element.execute(query);
        setError('');
      } catch (caught) {
        if (!cancelled) setError(caught instanceof Error ? caught.message : 'Unable to display job results.');
      }
    }

    void renderResults();
    return () => {
      cancelled = true;
      observer?.disconnect();
    };
  }, [elementName, profileId, query]);

  return (
    <div className="google-job-search" aria-live="polite">
      {error && <p className="notice">{error}</p>}
      <div ref={containerRef} className="google-job-search-results" />
    </div>
  );
}
