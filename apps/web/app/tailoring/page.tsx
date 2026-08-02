'use client';

import { FormEvent, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Change = {
  id: number;
  section: string;
  original_text: string;
  proposed_text: string;
  edited_text?: string | null;
  reason: string;
  evidence: Array<{type:string; id:number; text:string}>;
  status: string;
};

export default function TailoringPage() {
  const [proposalId, setProposalId] = useState('');
  const [changes, setChanges] = useState<Change[]>([]);
  const [unsupported, setUnsupported] = useState<string[]>([]);
  const token = typeof window !== 'undefined' ? localStorage.getItem('kall_token') : '';

  async function createProposal(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const response = await fetch(`${API}/api/tailoring/proposals`, {
      method: 'POST',
      headers: {'Content-Type':'application/json', Authorization:`Bearer ${token}`},
      body: JSON.stringify({job_id:Number(data.get('job_id')), professional_profile_id:Number(data.get('profile_id'))})
    });
    const proposal = await response.json();
    if (!response.ok) return alert(proposal.detail || 'Unable to create proposal');
    setProposalId(String(proposal.id));
    await load(String(proposal.id));
  }

  async function load(id = proposalId) {
    const response = await fetch(`${API}/api/tailoring/proposals/${id}`, {headers:{Authorization:`Bearer ${token}`}});
    const data = await response.json();
    if (!response.ok) return alert(data.detail || 'Unable to load proposal');
    setChanges(data.changes);
    setUnsupported(data.proposal.unsupported_requirements || []);
  }

  async function decide(change: Change, status: string, edited_text?: string) {
    const response = await fetch(`${API}/api/tailoring/changes/${change.id}`, {
      method:'PATCH',
      headers:{'Content-Type':'application/json', Authorization:`Bearer ${token}`},
      body:JSON.stringify({status, edited_text: edited_text || null})
    });
    const data = await response.json();
    if (!response.ok) return alert(data.detail || 'Unable to save decision');
    setChanges(current => current.map(item => item.id === data.id ? data : item));
  }

  return <main className="shell">
    <header className="topbar"><div className="brand">Kall Tailoring</div><nav><a href="/dashboard">Dashboard</a><a href="/job-intelligence">Job Intelligence</a></nav></header>
    <section className="card">
      <h1>Evidence-grounded tailoring</h1>
      <form className="form" onSubmit={createProposal}>
        <div className="two"><input className="input" name="job_id" placeholder="Job ID" required/><input className="input" name="profile_id" placeholder="Professional profile ID" required/></div>
        <button className="button">Create proposal</button>
      </form>
    </section>
    {unsupported.length > 0 && <section className="card"><h2>Unsupported requirements</h2><ul>{unsupported.map(item => <li key={item}>{item}</li>)}</ul></section>}
    {changes.map(change => <section className="card" key={change.id}>
      <span className="pill">{change.section}</span><h2>{change.reason}</h2>
      <div className="two"><div><h3>Original</h3><p>{change.original_text}</p></div><div><h3>Proposed</h3><textarea className="input" id={`edit-${change.id}`} defaultValue={change.edited_text || change.proposed_text} rows={8}/></div></div>
      <p><strong>Evidence:</strong> {change.evidence.map(item => item.text).join(' · ')}</p>
      <div style={{display:'flex',gap:10}}><button className="button" onClick={() => decide(change,'accepted')}>Accept</button><button className="button secondary" onClick={() => decide(change,'edited',(document.getElementById(`edit-${change.id}`) as HTMLTextAreaElement).value)}>Save edit</button><button className="button secondary" onClick={() => decide(change,'rejected')}>Reject</button></div>
      <p>Status: {change.status}</p>
    </section>)}
  </main>;
}
