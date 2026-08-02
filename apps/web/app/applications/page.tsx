import AppNav from '../components/AppNav';

const stages = [
  {
    title: 'Preparing',
    items: [
      { company: 'Northstar Health', role: 'Director, Quality Engineering', detail: 'Resume review ready', tone: 'accent' },
    ],
  },
  {
    title: 'Applied',
    items: [
      { company: 'Fjord Systems', role: 'Senior Director, Engineering Excellence', detail: 'Applied 2 days ago', tone: 'neutral' },
      { company: 'Quiet Works', role: 'Head of Quality Engineering', detail: 'Applied 5 days ago', tone: 'neutral' },
    ],
  },
  {
    title: 'Interview',
    items: [
      { company: 'Atlas Care', role: 'Director of Software Quality', detail: 'Thursday · 10:00 AM', tone: 'success' },
    ],
  },
  {
    title: 'Offer',
    items: [],
  },
];

export default function ApplicationsPage() {
  return (
    <main className="app-shell">
      <AppNav current="applications" />

      <section className="workspace-hero">
        <div>
          <p className="eyebrow">Application workspace</p>
          <h1>Four active conversations.</h1>
          <p>Review what needs attention without turning your career into a task board.</p>
        </div>
        <a className="button" href="/search">Find opportunities</a>
      </section>

      <section className="application-summary" aria-label="Application summary">
        <article><strong>4</strong><span>Active</span></article>
        <article><strong>1</strong><span>Interview</span></article>
        <article><strong>6 days</strong><span>Average response</span></article>
        <article><strong>92%</strong><span>Best match</span></article>
      </section>

      <section className="pipeline" aria-label="Application pipeline">
        {stages.map((stage) => (
          <section className="pipeline-column" key={stage.title}>
            <header>
              <h2>{stage.title}</h2>
              <span>{stage.items.length}</span>
            </header>
            <div className="pipeline-list">
              {stage.items.length ? stage.items.map((item) => (
                <article className="application-card" key={`${item.company}-${item.role}`}>
                  <span className={`status-dot ${item.tone}`} aria-hidden="true" />
                  <p>{item.company}</p>
                  <h3>{item.role}</h3>
                  <span>{item.detail}</span>
                  <a href="/job-intelligence">Open application</a>
                </article>
              )) : (
                <div className="pipeline-empty">No applications here.</div>
              )}
            </div>
          </section>
        ))}
      </section>

      <section className="application-focus calm-panel">
        <div>
          <p className="eyebrow">Next decision</p>
          <h2>Northstar Health is ready for review.</h2>
          <p>Kall prepared your director resume and highlighted two claims that need confirmation before application approval.</p>
        </div>
        <a className="button" href="/job-intelligence">Review preparation</a>
      </section>

      <p className="preview-note">Preview application data is shown until the application pipeline API is connected.</p>
    </main>
  );
}
