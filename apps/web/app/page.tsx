const modules = [
  [
    'Career identity',
    'A private, reusable record of your experience, achievements, preferences, and professional goals.',
  ],
  [
    'Opportunity intelligence',
    'Understand why a role fits, where the gaps are, and which experience best supports your candidacy.',
  ],
  [
    'Resume Studio',
    'Keep multiple resumes organized and prepare role-specific versions without losing your source history.',
  ],
  [
    'Application preparation',
    'Review every answer and document before Kall assists with a supported application workflow.',
  ],
  [
    'Career memory',
    'Capture accomplishments as they happen so your professional story stays current over time.',
  ],
  [
    'Across devices',
    'Continue the same career workflow on the web, desktop, and mobile without relearning the product.',
  ],
];

export default function Home() {
  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Kall home">
          Kall
        </a>
        <nav aria-label="Primary navigation">
          <a href="/search">Opportunities</a>
          <a href="/login">Log in</a>
          <a className="button" href="/onboarding">
            Get started
          </a>
        </nav>
      </header>

      <section className="hero">
        <span className="eyebrow">The Career Operating System</span>
        <h1>Build your life&apos;s work.</h1>
        <p>
          Kall brings your professional identity, opportunities, documents,
          applications, and career memory into one calm, private workspace.
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
          <a className="button" href="/onboarding">
            Create your Kall profile
          </a>
          <a className="button secondary" href="/job-intelligence">
            Explore match intelligence
          </a>
        </div>
      </section>

      <section aria-labelledby="platform-heading">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Built around the individual</span>
            <h2 id="platform-heading" style={{ marginTop: 14 }}>
              More than a job search.
            </h2>
          </div>
          <p>
            Kall is designed to support deliberate career decisions over years,
            not maximize applications or attention.
          </p>
        </div>

        <div className="grid">
          {modules.map(([title, body]) => (
            <article className="card" key={title}>
              <h2>{title}</h2>
              <p>{body}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
