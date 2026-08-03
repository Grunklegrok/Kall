'use client';

import Script from 'next/script';
import { FormEvent, useEffect, useState } from 'react';
import ProfessionalProfileSelect from '../components/ProfessionalProfileSelect';

const GOOGLE_CSE_ID = '551e53ca5b28b4060';

type AtsSearch = {
  query: string;
};

export default function SearchPage() {
  const [profileId, setProfileId] = useState('');
  const [query, setQuery] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const selectedProfile = params.get('profile');
    const selectedQuery = params.get('q');
    if (selectedProfile) setProfileId(selectedProfile);
    if (selectedQuery) setQuery(selectedQuery);
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

      const url = new URL(window.location.href);
      url.searchParams.set('q', finalQuery);
      if (profileId) url.searchParams.set('profile', profileId);
      else url.searchParams.delete('profile');
      window.location.assign(url.toString());
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Unable to start the job search.');
    } finally {
      setLoading(false);
    }
  }

  const hasSearch = typeof window !== 'undefined' && new URLSearchParams(window.location.search).has('q');

  return (
    <main className="shell">
      <Script
        src={`https://cse.google.com/cse.js?cx=${GOOGLE_CSE_ID}`}
        strategy="afterInteractive"
      />

      <header className="topbar">
        <a className="brand" href="/">Kall</a>
        <nav><a href="/opportunities">Opportunities</a><a href="/profiles">Profiles</a></nav>
      </header>

      <section className="hero" style={{ paddingBottom: 36 }}>
        <span className="eyebrow">Unified job search</span>
        <h1>Search the job market from one place.</h1>
        <p>Kall searches the ATS and public job sites configured in your Google Programmable Search Engine, including public LinkedIn job pages, and keeps the results inside Kall.</p>
      </section>

      <section className="card">
        <form className="form" onSubmit={searchJobs}>
          <div className="two">
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
          </div>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <button className="button" type="submit" disabled={loading}>
              {loading ? 'Preparing search…' : 'Search jobs'}
            </button>
            {hasSearch && (
              <a className="button ghost" href={profileId ? `/search?profile=${profileId}` : '/search'}>
                Clear results
              </a>
            )}
          </div>
        </form>
        <p className="notice" aria-live="polite" style={{ marginTop: 16 }}>{message}</p>
      </section>

      <section style={{ marginTop: 32 }}>
        <div className="section-heading">
          <div><span className="eyebrow">Results</span><h2 style={{ marginTop: 14 }}>Current job matches</h2></div>
          <p>Results are provided by Google Programmable Search and displayed directly inside Kall.</p>
        </div>
        <div className="card google-job-search">
          {hasSearch ? (
            <div className="gcse-searchresults-only" data-queryParameterName="q" />
          ) : (
            <div className="search-empty-state">
              <h2>No search results yet</h2>
              <p>Select a professional profile or enter a title, then press Search jobs.</p>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
