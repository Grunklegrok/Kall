'use client';

import { FormEvent, useEffect, useState } from 'react';

const API = '/api/kall';

type Opportunity = {
  id: number;
  job_id: number;
  state: string;
  match_score: number;
  notes?: string;
  last_seen_at: string;
};

export default function OpportunitiesPage() {
  const [items, setItems] = useState<Opportunity[]>([]);
  const [message, setMessage] = useState('');

  async function load(state = '') {
    const token = localStorage.getItem('kall_token');
    if (!token) {
      window.location.replace('/login');
      return;
    }
    const response = await fetch(`${API}/opportunities${state ? `?state=${state}` : ''}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.status === 401) {
      localStorage.removeItem('kall_token');
      window.location.replace('/login');
      return;
    }
    if (response.ok) {
      setItems(await response.json());
      setMessage('');
    } else {
      setMessage('Unable to load opportunities.');
    }
  }

  useEffect(() => { void load(); }, []);

  async function changeState(id: number, state: string) {
    const token = localStorage.getItem('kall_token');
    if (!token) {
      window.location.replace('/login');
      return;
    }
    const response = await fetch(`${API}/opportunities/${id}`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ state }),
    });
    if (response.status === 401) {
      localStorage.removeItem('kall_token');
      window.location.replace('/login');
      return;
    }
    setMessage(response.ok ? 'Opportunity updated.' : 'Unable to update opportunity.');
    if (response.ok) await load();
  }

  async function saveSchedule(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = localStorage.getItem('kall_token');
    if (!token) {
      window.location.replace('/login');
      return;
    }
    const form = new FormData(event.currentTarget);
    const response = await fetch(`${API}/discovery/schedules`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        professional_profile_id: Number(form.get('profile_id')),
        cadence: form.get('cadence'),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        hour_local: Number(form.get('hour_local')),
        max_posting_age_days: Number(form.get('age_days')),
      }),
    });
    if (response.status === 401) {
      localStorage.removeItem('kall_token');
      window.location.replace('/login');
      return;
    }
    setMessage(response.ok ? 'Discovery schedule saved.' : 'Unable to save schedule.');
  }

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="/">Kall</a>
        <nav aria-label="Opportunity navigation">
          <a href="/growth">Growth</a><a href="/job-intelligence">Intelligence</a><a href="/documents">Documents</a>
        </nav>
      </header>

      <section className="hero" style={{ paddingTop: 8, paddingBottom: 42 }}>
        <span className="eyebrow">Opportunity inbox</span>
        <h1 style={{ fontSize: 'clamp(44px, 7vw, 76px)' }}>A quieter way to find the right work.</h1>
        <p>Kall gathers new roles on your schedule, removes duplicates, and keeps every opportunity in a reviewable inbox.</p>
      </section>

      <section className="card">
        <h2>Schedule discovery</h2>
        <form className="form" onSubmit={saveSchedule}>
          <div className="two">
            <input className="input" name="profile_id" inputMode="numeric" placeholder="Professional profile ID" required />
            <select className="input" name="cadence" defaultValue="daily"><option value="daily">Daily</option><option value="weekdays">Weekdays</option><option value="weekly">Weekly</option></select>
          </div>
          <div className="two">
            <input className="input" name="hour_local" type="number" min="0" max="23" defaultValue="8" />
            <input className="input" name="age_days" type="number" min="1" max="90" defaultValue="30" />
          </div>
          <button className="button">Save schedule</button>
        </form>
        <p className="notice" aria-live="polite">{message}</p>
      </section>

      <section style={{ marginTop: 32 }}>
        <div className="section-heading"><div><span className="eyebrow">Inbox</span><h2 style={{ marginTop: 14 }}>Review what changed.</h2></div><p>Dismissed roles stay hidden unless the posting materially changes.</p></div>
        <div className="stack">
          {items.map((item) => (
            <article className="card" key={item.id}>
              <span className="pill">{item.state.replaceAll('_', ' ')}</span>
              <div className="metric"><strong>{item.match_score}%</strong><span className="muted">Job {item.job_id}</span></div>
              <p>Last seen {new Date(item.last_seen_at).toLocaleDateString()}</p>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 20 }}>
                <button className="button secondary" onClick={() => changeState(item.id, 'saved')}>Save</button>
                <button className="button secondary" onClick={() => changeState(item.id, 'reviewing')}>Review</button>
                <button className="button" onClick={() => changeState(item.id, 'apply')}>Apply</button>
                <button className="button ghost" onClick={() => changeState(item.id, 'not_interested')}>Dismiss</button>
              </div>
            </article>
          ))}
          {!items.length && <article className="card"><h2>No opportunities yet</h2><p>Create a schedule or run a search to begin filling your inbox.</p></article>}
        </div>
      </section>
    </main>
  );
}
