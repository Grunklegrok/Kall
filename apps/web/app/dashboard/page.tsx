const items = [
  ['Complete identity', 'Add websites, portfolios and contact preferences.', '/profile'],
  ['Create a professional profile', 'Choose industries, job titles, locations and compensation.', '/profiles'],
  ['Upload resumes', 'Build your Resume Studio and tag each version.', '/resumes'],
  ['Review privacy', 'Choose which fields can tailor, autofill or stay private.', '/privacy'],
] as const;

export default function Dashboard() {
  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="/">Kall</a>
        <nav>
          <a href="/profiles">Profiles</a>
          <a href="/resumes">Resume Studio</a>
        </nav>
      </header>
      <section className="hero">
        <span className="pill">Your workspace</span>
        <h1>Make your next move clear.</h1>
      </section>
      <div className="grid">
        {items.map(([title, description, href]) => (
          <a className="card" href={href} key={title} style={{ display: 'block', textDecoration: 'none' }}>
            <h2>{title}</h2>
            <p>{description}</p>
            <span className="muted">Open →</span>
          </a>
        ))}
      </div>
    </main>
  );
}
