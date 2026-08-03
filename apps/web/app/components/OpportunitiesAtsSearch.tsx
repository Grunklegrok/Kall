'use client';

import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';

type AtsSearch = {
  providers: string[];
  domains: string[];
  query: string;
  google_url: string;
  bing_url: string;
};

type ProfileEvent = CustomEvent<{ value: string }>;

export default function OpportunitiesAtsSearch() {
  const pathname = usePathname();
  const [profileId, setProfileId] = useState('');
  const [search, setSearch] = useState<AtsSearch | null>(null);
  const [message, setMessage] = useState('Select a professional profile to build its automated ATS Search.');
  const [loading, setLoading] = useState(false);
  const [engine, setEngine] = useState<'google' | 'bing' | null>(null);

  useEffect(() => {
    if (pathname !== '/opportunities') return;
    const listener = (event: Event) => {
      const value = (event as ProfileEvent).detail?.value || '';
      setProfileId(value);
      setSearch(null);
      setEngine(null);
    };
    window.addEventListener('kall:professional-profile-change', listener);
    return () => window.removeEventListener('kall:professional-profile-change', listener);
  }, [pathname]);

  useEffect(() => {
    if (pathname !== '/opportunities' || !profileId) return;
    const token = localStorage.getItem('kall_token');
    if (!token) return;
    setLoading(true);
    setMessage('Building the ATS query used by immediate and scheduled discovery…');
    fetch(`/api/kall/discovery/ats-search/${profileId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (response) => {
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Unable to build ATS Search.');
        return data;
      })
      .then((data) => {
        setSearch(data.queries?.[0] || null);
        setMessage('This ATS Search is included in Search Now and scheduled discovery for the selected profile.');
      })
      .catch((error) => setMessage(error instanceof Error ? error.message : 'Unable to build ATS Search.'))
      .finally(() => setLoading(false));
  }, [pathname, profileId]);

  if (pathname !== '/opportunities') return null;

  const searchUrl = engine === 'google' ? search?.google_url : search?.bing_url;

  return (
    <section className="shell" style={{ marginTop: 32, marginBottom: 32 }}>
      <article className="card">
        <div className="section-heading">
          <div><span className="eyebrow">Automated ATS Search</span><h2 style={{ marginTop: 14 }}>One query across ten ATS platforms</h2></div>
          <p>Used with structured company-board collectors during immediate and scheduled discovery.</p>
        </div>
        <p className="notice" aria-live="polite">{loading ? 'Building ATS Search…' : message}</p>
        {search && (
          <>
            <p className="muted" style={{ marginTop: 14 }}>{search.providers.join(' · ')}</p>
            <code style={{ display: 'block', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', marginTop: 14 }}>{search.query}</code>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 18 }}>
              <button className="button" type="button" onClick={() => setEngine(engine === 'google' ? null : 'google')}>Preview with Google</button>
              <button className="button secondary" type="button" onClick={() => setEngine(engine === 'bing' ? null : 'bing')}>Preview with Bing</button>
              <button className="button ghost" type="button" onClick={() => navigator.clipboard.writeText(search.query)}>Copy ATS Search</button>
              <a className="button ghost" href={`/search?profile=${profileId}`}>Open full ATS Search workspace</a>
            </div>
            {engine && searchUrl && (
              <div style={{ marginTop: 20 }}>
                <iframe
                  src={searchUrl}
                  title={`${engine} automated ATS Search preview`}
                  referrerPolicy="no-referrer"
                  sandbox="allow-forms allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"
                  style={{ width: '100%', minHeight: 520, border: '1px solid var(--border)', borderRadius: 18, background: '#fff' }}
                />
                <a className="button secondary" href={searchUrl} target="_blank" rel="noreferrer" style={{ marginTop: 12 }}>Open separately if embedding is blocked</a>
              </div>
            )}
          </>
        )}
      </article>
    </section>
  );
}
