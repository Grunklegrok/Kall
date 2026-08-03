'use client';

import { useEffect, useState } from 'react';

const API = '/api/kall';

type ResumeInsight = {
  id: number;
  name: string;
  version: number;
  is_default: boolean;
  tags: string[];
  industries: string[];
  target_titles: string[];
  readiness_score: number;
  strengths: string[];
  gaps: string[];
  aligned_profile_titles: string[];
  text_character_count: number;
};

type Dashboard = {
  summary: { resume_count: number; profile_count: number; best_resume_id?: number | null; best_score?: number | null; default_resume_id?: number | null };
  resumes: ResumeInsight[];
  profile_titles: string[];
};

export default function ResumeIntelligencePage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [message, setMessage] = useState('Loading resume intelligence…');

  useEffect(() => {
    const token = localStorage.getItem('kall_token');
    if (!token) return window.location.replace('/login');
    fetch(`${API}/me/resume-intelligence`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async response => {
        if (response.status === 401) {
          localStorage.removeItem('kall_token');
          window.location.replace('/login');
          throw new Error('signed-out');
        }
        if (!response.ok) throw new Error('Unable to load resume intelligence.');
        return response.json();
      })
      .then(result => { setData(result); setMessage(''); })
      .catch(error => { if (error.message !== 'signed-out') setMessage(error.message); });
  }, []);

  return <main className="shell">
    <header className="topbar"><a className="brand" href="/">Kall</a><nav><a href="/resumes">Resumes</a><a href="/profiles">Profiles</a><a href="/job-intelligence">Job Intelligence</a></nav></header>
    <section className="hero" style={{paddingTop:8,paddingBottom:42}}><span className="eyebrow">Resume intelligence</span><h1 style={{fontSize:'clamp(44px,7vw,76px)'}}>Know which resume is ready—and why.</h1><p>Kall reviews structure, targeting, searchable metadata, and alignment with your active professional profiles.</p></section>
    {message && <section className="card"><p>{message}</p></section>}
    {data && <>
      <section className="grid" aria-label="Resume intelligence summary">
        <article className="card"><h3>Resumes</h3><div className="metric"><strong>{data.summary.resume_count}</strong></div><p>available for matching</p></article>
        <article className="card"><h3>Best readiness</h3><div className="metric"><strong>{data.summary.best_score == null ? '—' : `${data.summary.best_score}%`}</strong></div><p>based on stored resume evidence</p></article>
        <article className="card"><h3>Target roles</h3><div className="metric"><strong>{data.profile_titles.length}</strong></div><p>across active profiles</p></article>
      </section>
      {!data.resumes.length ? <section className="card" style={{marginTop:24}}><h2>No resumes yet</h2><p>Upload a resume to begin evaluating readiness and role alignment.</p><a className="button" href="/resumes" style={{marginTop:18}}>Upload a resume</a></section> :
      <section style={{marginTop:32}}><div className="section-heading"><div><span className="eyebrow">Portfolio</span><h2 style={{marginTop:14}}>Your resume lineup</h2></div><p>Readiness is explainable and improves as you add targeting metadata and readable experience content.</p></div><div className="stack">
        {data.resumes.map(resume => <article className="card" key={resume.id}>
          <div style={{display:'flex',justifyContent:'space-between',gap:20,flexWrap:'wrap'}}><div><span className="pill">{resume.is_default ? 'Default resume' : `Version ${resume.version}`}</span><h2 style={{marginTop:14}}>{resume.name}</h2></div><div className="metric"><strong>{resume.readiness_score}%</strong><span className="muted">ready</span></div></div>
          <p>{resume.text_character_count.toLocaleString()} readable characters · {resume.aligned_profile_titles.length} aligned target role{resume.aligned_profile_titles.length === 1 ? '' : 's'}</p>
          <div className="two" style={{marginTop:22}}><div><h3>Strengths</h3><ul>{resume.strengths.map(item => <li key={item}>{item}</li>)}</ul></div><div><h3>Next improvements</h3><ul>{resume.gaps.length ? resume.gaps.map(item => <li key={item}>{item}</li>) : <li>No immediate metadata gaps detected.</li>}</ul></div></div>
          <a className="button secondary" href="/resumes" style={{marginTop:18}}>Edit resume details</a>
        </article>)}
      </div></section>}
    </>}
  </main>;
}
