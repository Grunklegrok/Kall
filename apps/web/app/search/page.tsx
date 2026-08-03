'use client';

import { useEffect, useState } from 'react';
import ProfessionalProfileSelect from '../components/ProfessionalProfileSelect';

type AtsSearch = {
  provider: string;
  domain: string;
  domains: string[];
  providers: string[];
  query: string;
  google_url: string;
  bing_url: string;
};

type SearchEngine = 'google' | 'bing';

export default function SearchPage() {
  const [profileId, setProfileId] = useState('');
  const [search, setSearch] = useState<AtsSearch | null>(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeEngine, setActiveEngine] = useState<SearchEngine | null>(null);

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
    setActiveEngine(null);
    setMessage('Building one unified ATS search…');
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
      if (!response.ok) throw new Error(data.detail || 'Unable to build ATS Search.');
      setSearch(data.queries?.[0] || null);
      setMessage(data.queries?.[0] ? 'ATS Search is ready.' : 'No ATS Search could be generated.');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Unable to build ATS Search.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (profileId && !search && !loading) void buildSearchPlan(profileId);
    // Build once for the selected profile; later changes are handled by the selector.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profileId]);

  const searchUrl = activeEngine === 'google' ? search?.google_url : search?.bing_url;

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="/">Kall</a>
        <nav><a href="/opportunities">Opportunities</a><a href="/profiles">Profiles</a></nav>
      </header>

      <section className="hero" style={{ paddingBottom: 36 }}>
        <span className="eyebrow">Hidden-market search</span>
        <h1>One ATS Search across the job boards search engines index.</h1>
        <p>Kall combines your target titles, skills, locations, remote preference, and exclusions into one Boolean query spanning the major ATS platforms.</p>
      </section>

      <section className="card">
        <div className="two">
          <ProfessionalProfileSelect
            value={profileId}
            onChange={(value) => {
              setProfileId(value);
              setSearch(null);
              setActiveEngine(null);
              const url = new URL(window.location.href);
              if (value) url.searchParams.set('profile', value);
              else url.searchParams.delete('profile');
              window.history.replaceState({}, '', url);
            }}
          />
          <div style={{ alignSelf: 'end' }}>
            <button className="button" type="button" disabled={!profileId || loading} onClick={() => buildSearchPlan()}>
              {loading ? 'Building ATS Search…' : 'Build ATS Search'}
            </button>
          </div>
        </div>
        <p className="notice" aria-live="polite" style={{ marginTop: 16 }}>{message}</p>
      </section>

      <section style={{ marginTop: 32 }}>
        <div className="section-heading">
          <div><span className="eyebrow">ATS Search</span><h2 style={{ marginTop: 14 }}>Unified Boolean query</h2></div>
          <p>One search covers Ashby, Greenhouse, Lever, iCIMS, Jobvite, Workday, BambooHR, SmartRecruiters, JazzHR, and Workable.</p>
        </div>

        {search ? (
          <article className="card">
            <span className="pill">ATS Search · {search.domains.length} platforms</span>
            <h2 style={{ marginTop: 14 }}>All supported ATS job pages</h2>
            <p className="muted">{search.providers.join(' · ')}</p>
            <code style={{ display: 'block', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', marginTop: 16 }}>{search.query}</code>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 18 }}>
              <button className="button" type="button" onClick={() => setActiveEngine(activeEngine === 'google' ? null : 'google')}>
                {activeEngine === 'google' ? 'Close Google module' : 'Search Google'}
              </button>
              <button className="button secondary" type="button" onClick={() => setActiveEngine(activeEngine === 'bing' ? null : 'bing')}>
                {activeEngine === 'bing' ? 'Close Bing module' : 'Search Bing'}
              </button>
              <button className="button ghost" type="button" onClick={() => navigator.clipboard.writeText(search.query)}>Copy ATS Search</button>
            </div>

            {activeEngine && searchUrl && (
              <section className="card" aria-label={`${activeEngine} ATS Search module`} style={{ marginTop: 22, padding: 18, background: 'var(--surface-subtle, rgba(255,255,255,0.02))' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
                  <div>
                    <span className="eyebrow">{activeEngine === 'google' ? 'Google' : 'Bing'} module</span>
                    <h3 style={{ marginTop: 10, marginBottom: 0 }}>Unified ATS Search</h3>
                  </div>
                  <button className="button ghost" type="button" onClick={() => setActiveEngine(null)}>Close module</button>
                </div>
                <p className="muted" style={{ marginTop: 12 }}>Results remain in this panel when the search engine permits embedding.</p>
                <iframe
                  key={activeEngine}
                  src={searchUrl}
                  title={`${activeEngine} unified ATS Search results`}
                  referrerPolicy="no-referrer"
                  sandbox="allow-forms allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"
                  style={{ width: '100%', minHeight: 620, border: '1px solid var(--border)', borderRadius: 18, marginTop: 16, background: '#fff' }}
                />
                <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 16 }}>
                  <a className="button secondary" href={searchUrl} target="_blank" rel="noreferrer">Open in a separate tab if blocked</a>
                  <button className="button ghost" type="button" onClick={() => navigator.clipboard.writeText(search.query)}>Copy ATS Search</button>
                </div>
              </section>
            )}
          </article>
        ) : !loading ? (
          <article className="card"><h2>No ATS Search yet</h2><p>Select a profile and build the unified search.</p></article>
        ) : null}
      </section>
    </main>
  );
}
