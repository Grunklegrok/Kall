'use client';

import { FormEvent, useEffect, useState } from 'react';
import ProfessionalProfileSelect from '../components/ProfessionalProfileSelect';
import GoogleJobSearchResults from '../components/GoogleJobSearchResults';

type AtsSearch = {
  query: string;
};

export default function SearchPage() {
  const [profileId, setProfileId] = useState('');
  const [query, setQuery] = useState('');
  const [activeQuery, setActiveQuery] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    document.documentElement.classList.add('search-page-active');
    document.body.classList.add('search-page-active');

    const params = new URLSearchParams(window.location.search);
    const selectedProfile = params.get('profile');
    const selectedQuery = params.get('q');
    if (selectedProfile) setProfileId(selectedProfile);
    if (selectedQuery) {
      setQuery(selectedQuery);
      setActiveQuery(selectedQuery);
    }

    return () => {
      document.documentElement.classList.remove('search-page-active');
      document.body.classList.remove('search-page-active');
    };
  }, []);

  async function buildProfileQuery(selectedProfile = profileId) {
    if (!selectedProfile) return '';
    const token = localStorage.getItem('kall_token');
    if (!token) {
      window.location.replace('/login');
      return '';
    }

    const response = await fetch(`/api/kall/discovery/ats-search/${selectedProfile}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.status === 401) {
      localStorage.removeItem('kall_token');
      window.location.replace('/login');
      return '';
    }
    const data = await response.json();
    if (!response.ok) {
      const detail = typeof data.detail === 'string' ? data.detail : 'Unable to build a profile search.';
      throw new Error(detail);
    }
    return (data.queries?.[0] as AtsSearch | undefined)?.query || '';
  }

  async function searchJobs(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage('Preparing your unified job search…');
    try {
      const generated = profileId ? await buildProfileQuery(profileId) : '';
      const finalQuery = query.trim() || generated.trim();
      if (!finalQuery) {
        setMessage('Enter a job title or select a professional profile.');
        return;
      }

      setQuery(finalQuery);
      setActiveQuery(finalQuery);
      const url = new URL(window.location.href);
      url.searchParams.set('q', finalQuery);
      if (profileId) url.searchParams.set('profile', profileId);
      else url.searchParams.delete('profile');
      window.history.replaceState({}, '', url);
      setMessage('Showing Google job results in the results column.');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Unable to start the job search.');
    } finally {
      setLoading(false);
    }
  }

  function clearResults() {
    setActiveQuery('');
    const url = new URL(window.location.href);
    url.searchParams.delete('q');
    window.history.replaceState({}, '', url);
    setMessage('Search results cleared.');
  }

  return (
    <main className="shell search-page-shell">
      <header className="topbar">
        <a className="brand" href="/">Kall</a>
        <nav><a href="/opportunities">Opportunities</a><a href="/profiles">Profiles</a></nav>
      </header>

      <section className="hero search-page-hero">
        <span className="eyebrow">Unified job search</span>
        <h1>Search the job market from one place.</h1>
        <p>Kall searches configured ATS and public job sites, including public LinkedIn job pages, and keeps the results inside Kall.</p>
      </section>

      <section className="search-page-columns" aria-label="Job search workspace">
        <article className="card search-page-controls-column">
          <div className="section-heading search-page-column-heading">
            <div>
              <span className="eyebrow">Search jobs</span>
              <h2 style={{ marginTop: 14 }}>Build your search</h2>
            </div>
          </div>

          <form className="form" onSubmit={searchJobs}>
            <ProfessionalProfileSelect
              value={profileId}
              onChange={(value) => {
                setProfileId(value);
                const url = new URL(window.location.href);
                if (value) url.searchParams.set('profile', value);
                else url.searchParams.delete('profile');
                window.history.replaceState({}, '', url);
              }}
              required={false}
            />
            <label>
              <span className="muted">Job title or search terms</span>
              <input
                className="input"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Director of Quality Engineering remote"
              />
            </label>
            <div className="search-page-actions">
              <button className="button" type="submit" disabled={loading}>
                {loading ? 'Preparing search…' : 'Search jobs'}
              </button>
              {activeQuery && <button className="button ghost" type="button" onClick={clearResults}>Clear results</button>}
            </div>
          </form>
          <p className="notice" aria-live="polite">{message}</p>
        </article>

        <article className="card search-page-results-column">
          <div className="section-heading search-page-column-heading">
            <div>
              <span className="eyebrow">Results</span>
              <h2 style={{ marginTop: 14 }}>Current job matches</h2>
            </div>
            <p>Results remain in this outlined Kall module.</p>
          </div>

          {activeQuery ? (
            <GoogleJobSearchResults query={activeQuery} />
          ) : (
            <div className="search-empty-state">
              <h2>No search results yet</h2>
              <p>Select a professional profile or enter a title, then press Search jobs.</p>
            </div>
          )}
        </article>
      </section>
    </main>
  );
}
