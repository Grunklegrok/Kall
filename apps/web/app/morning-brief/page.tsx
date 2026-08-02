import AppNav from '../components/AppNav';

const opportunities = [
  {
    title: 'Director, Quality Engineering',
    company: 'Northstar Health',
    location: 'Remote — United States',
    match: 94,
    reason: 'Strong alignment across leadership, automation strategy, and regulated software quality.',
  },
  {
    title: 'Senior Director, Engineering Excellence',
    company: 'Fjord Systems',
    location: 'Portland, OR · Hybrid',
    match: 91,
    reason: 'Your transformation and executive communication experience maps closely to the role.',
  },
  {
    title: 'Head of Quality Engineering',
    company: 'Quiet Works',
    location: 'Remote — United States',
    match: 89,
    reason: 'A strong fit for distributed leadership, quality platforms, and organizational scaling.',
  },
];

const health = [
  { label: 'Direction', value: 92, note: 'Your target role and leadership path are clearly defined.' },
  { label: 'Resume readiness', value: 88, note: 'Two leadership keywords could improve alignment.' },
  { label: 'Market alignment', value: 84, note: 'Your experience matches current quality leadership demand.' },
  { label: 'Network', value: 72, note: 'Reconnect with two former engineering leaders this month.' },
];

export default function MorningBriefPage() {
  return (
    <main className="app-shell">
      <AppNav current="brief" />

      <section className="brief-hero" aria-labelledby="brief-title">
        <p className="eyebrow">Sunday, August 2</p>
        <div className="brief-hero-grid">
          <div>
            <h1 id="brief-title">Good morning, James.</h1>
            <p className="brief-lede">Three opportunities deserve your attention today.</p>
          </div>
          <aside className="brief-summary" aria-label="Daily summary">
            <span>Daily focus</span>
            <strong>Review the top opportunity and approve a resume direction.</strong>
          </aside>
        </div>
      </section>

      <section className="brief-grid" aria-label="Career briefing">
        <div className="brief-main">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Prepared for you</p>
              <h2>Top opportunities</h2>
            </div>
            <a className="text-link" href="/search">View all opportunities</a>
          </div>

          <div className="opportunity-list">
            {opportunities.map((opportunity, index) => (
              <article className="opportunity-row" key={`${opportunity.company}-${opportunity.title}`}>
                <div className="opportunity-rank" aria-hidden="true">0{index + 1}</div>
                <div className="opportunity-copy">
                  <div className="opportunity-title-row">
                    <div>
                      <h3>{opportunity.title}</h3>
                      <p>{opportunity.company} · {opportunity.location}</p>
                    </div>
                    <span className="match-score">{opportunity.match}% match</span>
                  </div>
                  <p className="opportunity-reason">{opportunity.reason}</p>
                  <div className="inline-actions">
                    <a className="button button-small" href="/job-intelligence">Review analysis</a>
                    <button className="button-secondary button-small" type="button">Save for later</button>
                  </div>
                </div>
              </article>
            ))}
          </div>

          <article className="calm-panel interview-panel">
            <div>
              <p className="eyebrow">Upcoming</p>
              <h2>Interview preparation is ready.</h2>
              <p>Your leadership stories, company notes, and likely questions are organized for Thursday.</p>
            </div>
            <a className="button-secondary" href="/applications">Open interview plan</a>
          </article>
        </div>

        <aside className="brief-side">
          <article className="calm-panel">
            <p className="eyebrow">Career health</p>
            <div className="health-score-row">
              <strong>84</strong>
              <span>Strong</span>
            </div>
            <div className="health-list">
              {health.map((item) => (
                <div className="health-item" key={item.label}>
                  <div className="health-label-row">
                    <span>{item.label}</span>
                    <strong>{item.value}%</strong>
                  </div>
                  <div className="health-track" aria-label={`${item.label}: ${item.value}%`}>
                    <span style={{ width: `${item.value}%` }} />
                  </div>
                  <p>{item.note}</p>
                </div>
              ))}
            </div>
          </article>

          <article className="calm-panel">
            <p className="eyebrow">Quiet intelligence</p>
            <h2>Your director resume is the strongest starting point.</h2>
            <p>It currently covers 18 of 21 high-value signals across today’s top matches.</p>
            <a className="text-link" href="/resume-intelligence">Review resume evidence</a>
          </article>

          <p className="preview-note">Preview data is shown until the Morning Brief API is connected.</p>
        </aside>
      </section>
    </main>
  );
}
