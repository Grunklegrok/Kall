'use client';

import { FormEvent, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Question = { id: number; prompt: string; category: string; sensitive: boolean; required: boolean };
type Answer = { id: number; question_id: number; value?: string; status: string };
type ReviewData = { review: { status: string; readiness_issues: string[] }; questions: Question[]; answers: Answer[] };

export default function ApplicationReviewPage() {
  const [data, setData] = useState<ReviewData | null>(null);
  const [message, setMessage] = useState('');
  const [applicationId, setApplicationId] = useState('');

  async function load(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = localStorage.getItem('kall_token');
    const create = await fetch(`${API}/api/applications/${applicationId}/review`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
    if (!create.ok) return setMessage('Unable to create the review.');
    const response = await fetch(`${API}/api/applications/${applicationId}/review`, { headers: { Authorization: `Bearer ${token}` } });
    if (!response.ok) return setMessage('Unable to load the review.');
    setData(await response.json());
    setMessage('Review loaded.');
  }

  async function decide(answer: Answer, decision: string) {
    const token = localStorage.getItem('kall_token');
    const value = (document.getElementById(`answer-${answer.id}`) as HTMLInputElement)?.value || '';
    const response = await fetch(`${API}/api/applications/${applicationId}/answers/${answer.id}`, {
      method: 'PUT', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ value, value_json: {}, decision }),
    });
    setMessage(response.ok ? 'Answer decision saved.' : 'Unable to save answer.');
  }

  async function confirmAll() {
    const token = localStorage.getItem('kall_token');
    const response = await fetch(`${API}/api/applications/${applicationId}/review`, {
      method: 'PUT', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ documents_confirmed: true, answers_confirmed: true, sensitive_fields_confirmed: true, attestations_confirmed: true }),
    });
    setMessage(response.ok ? 'Review confirmations saved.' : 'Unable to confirm review.');
  }

  async function approve() {
    const token = localStorage.getItem('kall_token');
    const response = await fetch(`${API}/api/applications/${applicationId}/review/approve`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
    setMessage(response.ok ? 'Application approved for a future supported submission connector.' : 'Complete every review item before approval.');
  }

  return <main className="shell">
    <header className="topbar"><a className="brand" href="/">Kall</a><nav><a href="/opportunities">Opportunities</a><a href="/documents">Documents</a></nav></header>
    <section className="hero" style={{ paddingTop: 8, paddingBottom: 42 }}><span className="eyebrow">Application control</span><h1 style={{ fontSize: 'clamp(44px, 7vw, 76px)' }}>Review every answer before Kall acts.</h1><p>Confirm documents, screening answers, sensitive fields, and attestations. Approval never submits by itself.</p></section>
    <section className="card"><h2>Load application review</h2><form className="form" onSubmit={load}><input className="input" value={applicationId} onChange={e => setApplicationId(e.target.value)} placeholder="Application ID" required/><button className="button">Open review</button></form><p className="notice">{message}</p></section>
    {data && <div className="stack" style={{ marginTop: 16 }}>
      <section className="card"><span className="eyebrow">Readiness</span><div className="metric"><strong>{data.review.status}</strong></div><p>{data.review.readiness_issues?.join(' · ') || 'All required review items are complete.'}</p></section>
      {data.questions.map(question => { const answer = data.answers.find(item => item.question_id === question.id); return answer ? <article className="card" key={question.id}><span className="pill">{question.sensitive ? 'Sensitive — confirm' : question.category}</span><h2 style={{ marginTop: 16 }}>{question.prompt}</h2><input id={`answer-${answer.id}`} className="input" defaultValue={answer.value || ''}/><div style={{ display: 'flex', gap: 10, marginTop: 16, flexWrap: 'wrap' }}><button className="button" onClick={() => decide(answer, 'accepted')}>Accept</button><button className="button secondary" onClick={() => decide(answer, 'edited')}>Save edit</button><button className="button ghost" onClick={() => decide(answer, 'rejected')}>Reject</button></div></article> : null; })}
      <section className="card"><h2>Final confirmation</h2><p>Confirm the final documents, all answers, sensitive fields, and legal attestations before approving.</p><div style={{ display: 'flex', gap: 10, marginTop: 20, flexWrap: 'wrap' }}><button className="button secondary" onClick={confirmAll}>Confirm review items</button><button className="button" onClick={approve}>Approve application package</button></div></section>
    </div>}
  </main>;
}
