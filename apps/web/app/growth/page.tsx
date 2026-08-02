'use client';

import { FormEvent, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Milestone = { id: number; phase: string; title: string; description: string; estimated_hours?: number; status: string };
type Search = { id: number; category: string; query: string; search_url: string; rationale: string };
type Resource = { id: number; resource_type: string; title: string; url: string; description?: string };
type PlanResult = {
  plan: { id: number; summary: string; current_strengths: string[]; skill_gaps: string[]; recommended_roles: string[] };
  milestones: Milestone[];
  resources: Resource[];
  searches: Search[];
  completion_percent: number;
};

export default function GrowthPage() {
  const [result, setResult] = useState<PlanResult | null>(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  async function createPlan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage('Building your growth path…');
    const token = localStorage.getItem('kall_token');
    const form = new FormData(event.currentTarget);
    const goalResponse = await fetch(`${API}/api/growth/goals`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: form.get('title'),
        target_role: form.get('target_role'),
        target_industry: form.get('target_industry') || null,
        current_level: form.get('current_level') || null,
        target_level: form.get('target_level') || null,
        time_per_week_hours: Number(form.get('time_per_week_hours')) || null,
        budget_preference: form.get('budget_preference') || null,
        notes: form.get('notes') || null,
      }),
    });
    if (!goalResponse.ok) {
      setMessage('Kall could not save the career goal.');
      setLoading(false);
      return;
    }
    const goal = await goalResponse.json();
    const planResponse = await fetch(`${API}/api/growth/goals/${goal.id}/plan`, {
      method: 'POST', headers: { Authorization: `Bearer ${token}` },
    });
    if (!planResponse.ok) {
      setMessage('The goal was saved, but the plan could not be generated.');
      setLoading(false);
      return;
    }
    const plan = await planResponse.json();
    const detail = await fetch(`${API}/api/growth/plans/${plan.id}`, { headers: { Authorization: `Bearer ${token}` } });
    setResult(await detail.json());
    setMessage('Your direction is ready. Review it, then refine it as you learn.');
    setLoading(false);
  }

  async function completeMilestone(id: number) {
    const token = localStorage.getItem('kall_token');
    const response = await fetch(`${API}/api/growth/milestones/${id}`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'completed' }),
    });
    if (response.ok && result) {
      setResult({ ...result, milestones: result.milestones.map((item) => item.id === id ? { ...item, status: 'completed' } : item) });
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="/">Kall</a>
        <nav aria-label="Career growth navigation">
          <a href="/profile">Identity</a>
          <a href="/search">Opportunities</a>
          <a href="/documents">Documents</a>
        </nav>
      </header>

      <section className="hero" style={{ paddingTop: 8, paddingBottom: 42 }}>
        <span className="eyebrow">Career Growth &amp; Education</span>
        <h1 style={{ fontSize: 'clamp(44px, 7vw, 76px)' }}>Name the work you want. Build a path toward it.</h1>
        <p>Describe a role or field—such as game industry artist, product leader, or security engineer—and Kall turns it into a practical learning, portfolio, community, and market-research plan.</p>
      </section>

      <section className="card">
        <h2>Create a career direction</h2>
        <p style={{ marginBottom: 20 }}>The plan uses your existing Kall skills as starting evidence and keeps web research transparent through user-opened searches.</p>
        <form className="form" onSubmit={createPlan}>
          <div className="two">
            <label><span className="muted">Goal name</span><input className="input" name="title" placeholder="Move into game art" required /></label>
            <label><span className="muted">Target role</span><input className="input" name="target_role" placeholder="Game industry artist" required /></label>
          </div>
          <div className="two">
            <label><span className="muted">Industry or field</span><input className="input" name="target_industry" placeholder="Video games" /></label>
            <label><span className="muted">Hours available each week</span><input className="input" name="time_per_week_hours" type="number" min="1" max="80" placeholder="8" /></label>
          </div>
          <div className="two">
            <label><span className="muted">Current level</span><input className="input" name="current_level" placeholder="Beginner, adjacent professional…" /></label>
            <label><span className="muted">Target level</span><input className="input" name="target_level" placeholder="Entry level, senior, lead…" /></label>
          </div>
          <label><span className="muted">Learning budget</span><select className="input" name="budget_preference"><option value="free_first">Free resources first</option><option value="low_cost">Low cost</option><option value="open">Open to paid programs</option></select></label>
          <label><span className="muted">Context, constraints, or interests</span><textarea className="input" style={{ paddingTop: 12, minHeight: 110 }} name="notes" placeholder="I enjoy environment design and have experience with Photoshop…" /></label>
          <button className="button" disabled={loading}>{loading ? 'Building plan…' : 'Build my growth plan'}</button>
        </form>
        <p className="notice" aria-live="polite" style={{ marginTop: 16 }}>{message}</p>
      </section>

      {result && <div className="stack" style={{ marginTop: 16 }}>
        <section className="grid">
          <article className="card"><h3>Progress</h3><div className="metric"><strong>{result.completion_percent}%</strong><span className="muted">complete</span></div><p>{result.plan.summary}</p></article>
          <article className="card"><h3>Starting strengths</h3><p>{result.plan.current_strengths.join(' · ') || 'Add skills to your Kall profile to personalize this section.'}</p></article>
          <article className="card"><h3>Likely gaps</h3><p>{result.plan.skill_gaps.join(' · ')}</p></article>
        </section>

        <section>
          <div className="section-heading"><div><span className="eyebrow">Roadmap</span><h2 style={{ marginTop: 14 }}>A staged path, not a vague aspiration.</h2></div><p>Each stage creates evidence that can later feed Kall Identity, Resume Studio, and applications.</p></div>
          <div className="stack">{result.milestones.map((item) => <article className="card" key={item.id}><span className="pill">{item.phase}</span><h2 style={{ marginTop: 16 }}>{item.title}</h2><p>{item.description}</p><p style={{ marginTop: 12 }}>{item.estimated_hours ? `Estimated effort: ${item.estimated_hours} hours` : ''}</p><button className="button secondary" style={{ marginTop: 18 }} disabled={item.status === 'completed'} onClick={() => completeMilestone(item.id)}>{item.status === 'completed' ? 'Completed' : 'Mark complete'}</button></article>)}</div>
        </section>

        <section>
          <div className="section-heading"><div><span className="eyebrow">Live research prompts</span><h2 style={{ marginTop: 14 }}>Explore the field with intent.</h2></div><p>Searches open in a new tab so sources remain visible and users decide what to trust or save.</p></div>
          <div className="grid">{result.searches.map((item) => <article className="card" key={item.id}><h3>{item.category.replaceAll('_', ' ')}</h3><h2>{item.query}</h2><p>{item.rationale}</p><a className="button secondary" style={{ marginTop: 18 }} href={item.search_url} target="_blank" rel="noreferrer">Run web search</a></article>)}</div>
        </section>

        <section className="card"><span className="eyebrow">Adjacent paths</span><h2 style={{ marginTop: 16 }}>Roles worth comparing</h2><p>{result.plan.recommended_roles.join(' · ')}</p></section>
      </div>}
    </main>
  );
}
