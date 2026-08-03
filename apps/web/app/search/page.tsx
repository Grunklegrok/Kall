'use client';

import { useState } from 'react';
import ProfessionalProfileSelect from '../components/ProfessionalProfileSelect';

type AtsQuery = {
  provider: string;
  domain: string;
  query: string;
  google_url: string;
  bing_url: string;
};

export default function SearchPage() {
  const [profileId, setProfileId] = useState('');
  const [queries, setQueries] = useState<AtsQuery[]>([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  async function buildSearchPlan() {
    if (!profileId) {
      setMessage('Select a professional profile first.');
      return;
    }
    const token = localStorage.getItem('kall_token');
    if (!token) {
      window.location.replace('/login');
      return;
    }
    setLoading(true);
    setMessage('Building ATS-specific Boolean searches…');
    try {
      const response = await fetch(`/api/kall/discovery/ats-search/${profileId}`, {
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
          <ProfessionalProfileSelect value={profileId} onChange={setProfileId} />
          <div style={{ alignSelf: 'end' }}>
            <button className="button" type="button" disabled={!profileId || loading} onClick={buildSearchPlan}>
              {loading ? 'Building searches…' : 'Build ATS searches'}
            </button>
          </div>
        </div>
        <p className="notice" aria-live="polite" style={{ marginTop: 16 }}>{message}</p>
      </section>

      <section style={{ marginTop: 32 }}>
        <div className="section-heading">
          <div><span className="eyebrow">Search plan</span><h2 style={{ marginTop: 14 }}>ATS-specific queries</h2></div>
          <p>Open searches individually to review fresh, less-visible listings directly in Google or Bing.</p>
        </div>
        <div className="stack">
          {queries.map((item) => (
            <article className="card" key={item.domain}>
              <span className="pill">{item.provider}</span>
              <h2 style={{ marginTop: 14 }}>{item.domain}</h2>
              <code style={{ display: 'block', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', marginTop: 12 }}>{item.query}</code>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 18 }}>
                <a className="button" href={item.google_url} target="_blank" rel="noreferrer">Search Google</a>
                <a className="button secondary" href={item.bing_url} target="_blank" rel="noreferrer">Search Bing</a>
                <button className="button ghost" type="button" onClick={() => navigator.clipboard.writeText(item.query)}>Copy query</button>
              </div>
            </article>
          ))}
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
