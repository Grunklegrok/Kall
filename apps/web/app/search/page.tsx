'use client';

import { useEffect, useState } from 'react';
import ProfessionalProfileSelect from '../components/ProfessionalProfileSelect';

type AtsQuery = {
  provider: string;
  domain: string;
  query: string;
  google_url: string;
  bing_url: string;
};

type SearchEngine = 'google' | 'bing';

type ActiveSearch = {
  domain: string;
  engine: SearchEngine;
};

export default function SearchPage() {
  const [profileId, setProfileId] = useState('');
  const [queries, setQueries] = useState<AtsQuery[]>([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeSearch, setActiveSearch] = useState<ActiveSearch | null>(null);

  useEffect(() => {
    const selectedProfile = new URLSearchParams(window.location.search).get('profile');
    if (selectedProfile) setProfileId(selectedProfile);
  }, []);

  async function buildSearchPlan(selectedProfile = profileId) {
    if (!selectedProfile) {
      setMessage('Select a professional profile first.');
      return;
    }
    const token = localStorage.getItem('kall_token');
    if (!token) {
      window.location.replace('/login');
      return;
    }
    setLoading(true);
    setActiveSearch(null);
    setMessage('Building ATS-specific Boolean searches…');
    try {
      const response = await fetch(`/api/kall/discovery/ats-search/${selectedProfile}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.status === 401) {
        localStorage.removeItem('kall_token');
        window.location.replace('/login');
        return;
      }
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Unable to build the search plan.');
      setQueries(data.queries || []);
      setMessage(`${data.queries?.length || 0} ATS searches are ready.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Unable to build the search plan.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (profileId && queries.length === 0 && !loading) void buildSearchPlan(profileId);
    // The first selected profile should build once; later changes are handled explicitly.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profileId]);

  function openModule(domain: string, engine: SearchEngine) {
    setActiveSearch((current) => (
      current?.domain === domain && current.engine === engine ? null : { domain, engine }
    ));
  }

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="/">Kall</a>
        <nav><a href="/opportunities">Opportunities</a><a href="/profiles">Profiles</a></nav>
      </header>

      <section className="hero" style={{ paddingBottom: 36 }}>
        <span className="eyebrow">Hidden-market search</span>
        <h1>Search the job boards that search engines index.</h1>
        <p>Kall builds site-restricted Boolean searches from your target titles, skills, locations, remote preference, and excluded keywords.</p>
      </section>

      <section className="card">
        <div className="two">
          <ProfessionalProfileSelect
            value={profileId}
            onChange={(value) => {
              setProfileId(value);
              setQueries([]);
              setActiveSearch(null);
              const url = new URL(window.location.href);
              if (value) url.searchParams.set('profile', value);
              else url.searchParams.delete('profile');
              window.history.replaceState({}, '', url);
            }}
          />
          <div style={{ alignSelf: 'end' }}>
            <button className="button" type="button" disabled={!profileId || loading} onClick={() => buildSearchPlan()}>
              {loading ? 'Building searches…' : 'Build ATS searches'}
            </button>
          </div>
        </div>
        <p className="notice" aria-live="polite" style={{ marginTop: 16 }}>{message}</p>
      </section>

      <section style={{ marginTop: 32 }}>
        <div className="section-heading">
          <div><span className="eyebrow">Search plan</span><h2 style={{ marginTop: 14 }}>ATS-specific queries</h2></div>
          <p>Choose an engine to open its search module directly inside the matching ATS card.</p>
        </div>
        <div className="stack">
          {queries.map((item) => {
            const moduleOpen = activeSearch?.domain === item.domain;
            const engine = moduleOpen ? activeSearch.engine : null;
            const searchUrl = engine === 'google' ? item.google_url : item.bing_url;

            return (
              <article className="card" key={item.domain}>
                <span className="pill">{item.provider}</span>
                <h2 style={{ marginTop: 14 }}>{item.domain}</h2>
                <code style={{ display: 'block', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', marginTop: 12 }}>{item.query}</code>
                <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 18 }}>
                  <button className="button" type="button" onClick={() => openModule(item.domain, 'google')}>
                    {moduleOpen && engine === 'google' ? 'Close Google module' : 'Search Google'}
                  </button>
                  <button className="button secondary" type="button" onClick={() => openModule(item.domain, 'bing')}>
                    {moduleOpen && engine === 'bing' ? 'Close Bing module' : 'Search Bing'}
                  </button>
                  <button className="button ghost" type="button" onClick={() => navigator.clipboard.writeText(item.query)}>Copy query</button>
                </div>

                {moduleOpen && engine && (
                  <section
                    className="card"
                    aria-label={`${item.provider} ${engine} search module`}
                    style={{ marginTop: 22, padding: 18, background: 'var(--surface-subtle, rgba(255,255,255,0.02))' }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
                      <div>
                        <span className="eyebrow">{engine === 'google' ? 'Google' : 'Bing'} module</span>
                        <h3 style={{ marginTop: 10, marginBottom: 0 }}>{item.provider} search</h3>
                      </div>
                      <button className="button ghost" type="button" onClick={() => setActiveSearch(null)}>Close module</button>
                    </div>

                    <p className="muted" style={{ marginTop: 12 }}>
                      Search results remain inside this panel when the search engine permits embedding. Some engines block embedded result pages for security reasons.
                    </p>

                    <iframe
                      key={`${item.domain}-${engine}`}
                      src={searchUrl}
                      title={`${engine} results for ${item.provider}`}
                      referrerPolicy="no-referrer"
                      sandbox="allow-forms allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"
                      style={{ width: '100%', minHeight: 620, border: '1px solid var(--border)', borderRadius: 18, marginTop: 16, background: '#fff' }}
                    />

                    <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 16 }}>
                      <a className="button secondary" href={searchUrl} target="_blank" rel="noreferrer">
                        Open in a separate tab if blocked
                      </a>
                      <button className="button ghost" type="button" onClick={() => navigator.clipboard.writeText(item.query)}>Copy this query</button>
                    </div>
                  </section>
                )}
              </article>
            );
          })}
          {!loading && queries.length === 0 && (
            <article className="card">
              <h2>No search plan yet</h2>
              <p>Select a profile and build searches. Kall will generate queries for Ashby, Greenhouse, Lever, iCIMS, Jobvite, Workday, BambooHR, SmartRecruiters, JazzHR, and Workable.</p>
            </article>
          )}
        </div>
      </section>
    </main>
  );
}
