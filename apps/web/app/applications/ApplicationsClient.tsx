'use client';

import { useEffect, useState } from 'react';
import AppNav from '../components/AppNav';
import styles from './page.module.css';

const API = '/api/kall';

type PipelineItem = {
  id: number;
  status: string;
  stage: string;
  company: string;
  role: string;
  location?: string | null;
  match_score?: number | null;
  updated_at?: string | null;
  submitted_at?: string | null;
  requires_review: boolean;
  unanswered_question_count: number;
  sensitive_fields_present: boolean;
  failure_reason?: string | null;
};

type Stage = { key: string; label: string; count: number; items: PipelineItem[] };
type Pipeline = {
  summary: { total: number; active: number; needs_review: number; submitted: number; best_match?: number | null };
  stages: Stage[];
  next_decision?: PipelineItem | null;
  generated_at: string;
};

function isPipeline(value: unknown): value is Pipeline {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<Pipeline>;
  return Boolean(
    candidate.summary &&
      typeof candidate.summary.total === 'number' &&
      typeof candidate.summary.active === 'number' &&
      typeof candidate.summary.needs_review === 'number' &&
      typeof candidate.summary.submitted === 'number' &&
      Array.isArray(candidate.stages) &&
      candidate.stages.every(
        stage =>
          stage &&
          typeof stage.key === 'string' &&
          typeof stage.label === 'string' &&
          typeof stage.count === 'number' &&
          Array.isArray(stage.items),
      ),
  );
}

function relativeTime(value?: string | null) {
  if (!value) return 'Recently updated';
  const milliseconds = Date.now() - new Date(value).getTime();
  const days = Math.max(0, Math.floor(milliseconds / 86_400_000));
  if (days === 0) return 'Updated today';
  return `Updated ${days} day${days === 1 ? '' : 's'} ago`;
}

function detail(item: PipelineItem) {
  if (item.failure_reason) return item.failure_reason;
  if (item.requires_review) {
    const reasons = [
      item.unanswered_question_count ? `${item.unanswered_question_count} unanswered` : null,
      item.sensitive_fields_present ? 'sensitive fields require confirmation' : null,
    ].filter(Boolean);
    return reasons.join(' · ') || 'Review required before approval';
  }
  if (item.submitted_at) return `Submitted ${new Date(item.submitted_at).toLocaleDateString()}`;
  return relativeTime(item.updated_at);
}

export default function ApplicationsClient() {
  const [pipeline, setPipeline] = useState<Pipeline | null>(null);
  const [state, setState] = useState<'loading' | 'ready' | 'signed-out' | 'error'>('loading');
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('kall_token');
    if (!token) {
      setState('signed-out');
      return;
    }

    fetch(`${API}/me/applications`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async response => {
        if (response.status === 401) {
          localStorage.removeItem('kall_token');
          throw new Error('signed-out');
        }
        if (!response.ok) {
          let detail = `The applications API returned ${response.status}.`;
          try {
            const data = await response.json();
            if (typeof data.detail === 'string') detail = data.detail;
          } catch {
            // Preserve the status-based message for non-JSON responses.
          }
          throw new Error(detail);
        }
        return response.json();
      })
      .then(data => {
        if (!isPipeline(data)) throw new Error('The applications API returned an unexpected response.');
        setPipeline(data);
        setState('ready');
      })
      .catch(caught => {
        if (caught instanceof Error && caught.message === 'signed-out') {
          setState('signed-out');
          return;
        }
        setError(caught instanceof Error ? caught.message : 'Unable to load applications.');
        setState('error');
      });
  }, []);

  if (state === 'loading') {
    return <main className='app-shell'><AppNav current='applications'/><section className={styles.hero}><div><p className='eyebrow'>Application workspace</p><h1>Gathering your pipeline.</h1><p>Kall is reviewing your current application records.</p></div></section></main>;
  }

  if (state === 'signed-out') {
    return <main className='app-shell'><AppNav current='applications'/><section className={styles.hero}><div><p className='eyebrow'>Application workspace</p><h1>Sign in to view your applications.</h1><p>Your application history and review queue remain private to your account.</p></div><a className='button' href='/login'>Sign in</a></section></main>;
  }

  if (state === 'error' || !pipeline) {
    return <main className='app-shell'><AppNav current='applications'/><section className={styles.hero}><div><p className='eyebrow'>Application workspace</p><h1>Your pipeline could not be loaded.</h1><p>{error || 'The API did not return a usable response. Your stored application data was not changed.'}</p></div><button className='button' onClick={() => location.reload()}>Try again</button></section></main>;
  }

  const hasApplications = pipeline.summary.total > 0;
  const next = pipeline.next_decision;

  return <main className='app-shell'>
    <AppNav current='applications'/>
    <section className={styles.hero}>
      <div>
        <p className='eyebrow'>Application workspace</p>
        <h1>{hasApplications ? `${pipeline.summary.active} active application${pipeline.summary.active === 1 ? '' : 's'}.` : 'Your pipeline is ready.'}</h1>
        <p>{hasApplications ? 'Review what needs attention without turning your career into a task board.' : 'Prepare an application from a matched opportunity to begin tracking it here.'}</p>
      </div>
      <a className='button' href='/search'>Find opportunities</a>
    </section>

    <section className={styles.summary} aria-label='Application summary'>
      <article><strong>{pipeline.summary.active}</strong><span>Active</span></article>
      <article><strong>{pipeline.summary.needs_review}</strong><span>Needs review</span></article>
      <article><strong>{pipeline.summary.submitted}</strong><span>Submitted</span></article>
      <article><strong>{pipeline.summary.best_match == null ? '—' : `${pipeline.summary.best_match}%`}</strong><span>Best match</span></article>
    </section>

    <section className={styles.pipeline} aria-label='Application pipeline'>
      {pipeline.stages.map(stage => <section className={styles.column} key={stage.key}>
        <header><h2>{stage.label}</h2><span>{stage.count}</span></header>
        <div className={styles.list}>
          {stage.items.length ? stage.items.map(item => <article className={styles.card} key={item.id}>
            <span className={`${styles.dot} ${item.requires_review ? styles.accent : item.stage === 'submitted' ? styles.success : ''}`} aria-hidden='true'/>
            <p>{item.company}{item.location ? ` · ${item.location}` : ''}</p>
            <h3>{item.role}</h3>
            <span>{detail(item)}{item.match_score == null ? '' : ` · ${item.match_score}% match`}</span>
            <a href={`/job-intelligence?application=${item.id}`}>Open application</a>
          </article>) : <div className={styles.empty}>No applications here.</div>}
        </div>
      </section>)}
    </section>

    {next ? <section className={`${styles.focus} card`}>
      <div><p className='eyebrow'>Next decision</p><h2>{next.company} is ready for review.</h2><p>{detail(next)}. Kall will not approve or submit it without your confirmation.</p></div>
      <a className='button' href={`/job-intelligence?application=${next.id}`}>Review preparation</a>
    </section> : <section className={`${styles.focus} card`}>
      <div><p className='eyebrow'>Next decision</p><h2>No application needs your approval.</h2><p>Kall will surface the next review here when a prepared application requires confirmation.</p></div>
      <a className='button secondary' href='/morning-brief'>Return to Morning Brief</a>
    </section>}

    <p className={styles.note}>Pipeline data is loaded from your stored Kall applications. Interview and offer stages will appear only after those records are modeled and captured.</p>
  </main>;
}
