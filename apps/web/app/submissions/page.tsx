'use client';

import { FormEvent, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Submission = { id: number; status: string; provider: string; preview_json: Record<string, unknown>; failure_detail?: string; manual_url?: string };

export default function SubmissionsPage() {
  const [applicationId, setApplicationId] = useState('');
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [message, setMessage] = useState('');

  async function prepare(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = localStorage.getItem('kall_token');
    const response = await fetch(`${API}/api/applications/${applicationId}/submission-preview`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
    if (!response.ok) return setMessage('Unable to prepare a submission preview.');
    setSubmission(await response.json());
    setMessage('Immutable preview prepared. Review every field before confirming.');
  }

  async function confirm() {
    if (!submission) return;
    const token = localStorage.getItem('kall_token');
    const response = await fetch(`${API}/api/submissions/${submission.id}/confirm`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
    const body = await response.json();
    setSubmission(body);
    setMessage(body.status === 'confirmed' ? 'Submission confirmed. A fresh attempt may now be created.' : body.failure_detail || 'Submission blocked.');
  }

  async function attempt() {
    if (!submission) return;
    const token = localStorage.getItem('kall_token');
    const response = await fetch(`${API}/api/submissions/${submission.id}/attempt`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
    setMessage(response.ok ? 'Idempotent submission attempt created. Provider transport remains controlled by the connector adapter.' : 'A fresh confirmation is required.');
  }

  return <main className="shell">
    <header className="topbar"><a className="brand" href="/">Kall</a><nav><a href="/application-review">Application review</a><a href="/opportunities">Opportunities</a></nav></header>
    <section className="hero" style={{ paddingTop: 8, paddingBottom: 42 }}><span className="eyebrow">Submission control</span><h1 style={{ fontSize: 'clamp(44px, 7vw, 76px)' }}>Nothing is submitted without a fresh confirmation.</h1><p>Review the exact documents, answers, sensitive fields, testimonials, connector, and manual fallbacks before Kall creates an attempt.</p></section>
    <section className="card"><form className="form" onSubmit={prepare}><input className="input" value={applicationId} onChange={e => setApplicationId(e.target.value)} placeholder="Application ID" required/><button className="button">Prepare immutable preview</button></form><p className="notice">{message}</p></section>
    {submission && <div className="stack" style={{ marginTop: 16 }}><section className="card"><span className="pill">{submission.provider}</span><h2 style={{ marginTop: 16 }}>{submission.status}</h2><pre style={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>{JSON.stringify(submission.preview_json, null, 2)}</pre>{submission.failure_detail && <p className="notice">{submission.failure_detail}</p>}<div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}><button className="button secondary" onClick={confirm}>Confirm exact preview</button><button className="button" onClick={attempt} disabled={submission.status !== 'confirmed'}>Create submission attempt</button>{submission.manual_url && <a className="button ghost" href={submission.manual_url}>Open manual application</a>}</div></section></div>}
  </main>;
}
