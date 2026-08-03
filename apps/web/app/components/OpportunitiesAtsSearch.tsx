'use client';

import Script from 'next/script';
import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';

const GOOGLE_CSE_ID = '551e53ca5b28b4060';

type AtsSearch = { query: string };
type ProfileEvent = CustomEvent<{ value: string }>;

export default function OpportunitiesAtsSearch() {
  const pathname = usePathname();
  const [profileId, setProfileId] = useState('');
  const [search, setSearch] = useState<AtsSearch | null>(null);
  const [message, setMessage] = useState('Select a professional profile to prepare its unified job search.');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (pathname !== '/opportunities') return;
    const params = new URLSearchParams(window.location.search);
    const profile = params.get('profile');
    if (profile) setProfileId(profile);

    const listener = (event: Event) => {
      const value = (event as ProfileEvent).detail?.value || '';
      setProfileId(value);
      setSearch(null);
    };
    window.addEventListener('kall:professional-profile-change', listener);
    return () => window.removeEventListener('kall:professional-profile-change', listener);
  }, [pathname]);

  useEffect(() => {
    if (pathname !== '/opportunities' || !profileId) return;
    const token = localStorage.getItem('kall_token');
    if (!token) return;
    setLoading(true);
    setMessage('Preparing the Google Programmable Search query…');
    fetch(`/api/kall/discovery/ats-search/${profileId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (response) => {
        const data = await response.json();
        if (!response.ok) {
          const detail = typeof data.detail === 'string' ? data.detail : 'Unable to prepare job search.';
          throw new Error(detail);
        }
        return data;
      })
      .then((data) => {
        setSearch(data.queries?.[0] || null);
        setMessage('Your unified search is ready.');
      })
      .catch((error) => setMessage(error instanceof Error ? error.message : 'Unable to prepare job search.'))
      .finally(() => setLoading(false));
  }, [pathname, profileId]);

  if (pathname !== '/opportunities') return null;

  const hasResults = typeof window !== 'undefined' && new URLSearchParams(window.location.search).has('q');

  function searchJobs() {
    if (!search?.query || !profileId) {
      setMessage('Select a profile before searching.');
      return;
    }
    const url = new URL(window.location.href);
    url.searchParams.set('profile', profileId);
    url.searchParams.set('q', search.query);
    window.location.assign(url.toString());
  }

  return (
    <section className="shell" style={{ marginTop: 32, marginBottom: 32 }}>
      <Script src={`https://cse.google.com/cse.js?cx=${GOOGLE_CSE_ID}`} strategy="afterInteractive" />
      <article className="card">
        <div className="section-heading">
          <div><span className="eyebrow">Unified job search</span><h2 style={{ marginTop: 14 }}>Search every configured job source</h2></div>
          <p>Google Programmable Search covers the ATS domains and public LinkedIn job pages configured in search engine {GOOGLE_CSE_ID}.</p>
        </div>
        <p className="notice" aria-live="polite">{loading ? 'Preparing search…' : message}</p>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 18 }}>
          <button className="button" type="button" onClick={searchJobs} disabled={!search || loading}>
            Search jobs
          </button>
          <a className="button ghost" href={profileId ? `/search?profile=${profileId}` : '/search'}>
            Open search workspace
          </a>
          {hasResults && <a className="button ghost" href={`/opportunities?profile=${profileId}`}>Clear results</a>}
        </div>

        {hasResults && (
          <div className="google-job-search" style={{ marginTop: 24 }}>
            <div className="gcse-searchresults-only" data-queryParameterName="q" />
          </div>
        )}
      </article>
    </section>
  );
}
