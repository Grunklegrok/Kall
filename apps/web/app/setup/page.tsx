'use client';

import { useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const steps = ['identity', 'preferences', 'resume', 'experience', 'authorization', 'privacy', 'ready'];

export default function SetupPage() {
  const [current, setCurrent] = useState('identity');
  const [completed, setCompleted] = useState<string[]>([]);
  const [readiness, setReadiness] = useState<any>(null);
  const token = () => localStorage.getItem('kall_token');

  async function load() {
    const headers = { Authorization: `Bearer ${token()}` };
    const [progressResponse, readinessResponse] = await Promise.all([
      fetch(`${API}/api/profile/onboarding`, { headers }),
      fetch(`${API}/api/profile/readiness`, { headers }),
    ]);
    if (progressResponse.ok) {
      const progress = await progressResponse.json();
      setCurrent(progress.current_step);
      setCompleted(progress.completed_steps);
    }
    if (readinessResponse.ok) setReadiness(await readinessResponse.json());
  }

  useEffect(() => { load(); }, []);

  async function complete(step: string) {
    const nextCompleted = Array.from(new Set([...completed, step]));
    const next = steps[Math.min(steps.indexOf(step) + 1, steps.length - 1)];
    const response = await fetch(`${API}/api/profile/onboarding`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` },
      body: JSON.stringify({
        current_step: next,
        completed_steps: nextCompleted,
        dismissed_steps: [],
        is_complete: next === 'ready',
      }),
    });
    if (response.ok) {
      setCompleted(nextCompleted);
      setCurrent(next);
      load();
    }
  }

  const destinations: Record<string, string> = {
    identity: '/profile',
    preferences: '/profiles',
    resume: '/resumes',
    experience: '/profile-details',
    authorization: '/privacy',
    privacy: '/privacy',
    ready: '/dashboard',
  };

  return <main className="shell">
    <header className="topbar"><div className="brand">Kall Setup</div><a href="/dashboard">Dashboard</a></header>
    <section className="card">
      <span className="pill">Application readiness {readiness?.overall ?? 0}%</span>
      <h1>Build your complete career identity</h1>
      <p>Finish each section once. Kall reuses only the information and privacy scopes you approve.</p>
      <div className="grid">
        {steps.map((step, index) => <article className="card" key={step} style={{ opacity: current === step || completed.includes(step) ? 1 : .65 }}>
          <b>{index + 1}. {step.replace('_', ' ')}</b>
          <p>{completed.includes(step) ? 'Complete' : current === step ? 'Current step' : 'Not started'}</p>
          <a className="button secondary" href={destinations[step]}>Open section</a>{' '}
          {!completed.includes(step) && <button className="button" onClick={() => complete(step)}>Mark complete</button>}
        </article>)}
      </div>
      {readiness && <div style={{ marginTop: 24 }}><h2>Readiness details</h2>{Object.entries(readiness.sections).map(([name, score]) => <p key={name}><b>{name.replace('_', ' ')}</b>: {String(score)}%</p>)}</div>}
    </section>
  </main>;
}
