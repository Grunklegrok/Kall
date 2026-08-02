type AppNavProps = {
  current?: 'brief' | 'opportunities' | 'applications' | 'documents' | 'career';
};

const items = [
  { key: 'brief', label: 'Brief', href: '/morning-brief' },
  { key: 'opportunities', label: 'Opportunities', href: '/search' },
  { key: 'applications', label: 'Applications', href: '/applications' },
  { key: 'documents', label: 'Documents', href: '/resume-intelligence' },
  { key: 'career', label: 'Career', href: '/profiles' },
] as const;

export default function AppNav({ current }: AppNavProps) {
  return (
    <header className="app-header">
      <a className="app-brand" href="/" aria-label="Kall home">
        Kall
      </a>
      <nav className="app-nav" aria-label="Primary navigation">
        {items.map((item) => (
          <a
            key={item.key}
            href={item.href}
            className={current === item.key ? 'app-nav-link is-active' : 'app-nav-link'}
            aria-current={current === item.key ? 'page' : undefined}
          >
            {item.label}
          </a>
        ))}
      </nav>
      <a className="app-account" href="/settings" aria-label="Open account settings">
        JS
      </a>
    </header>
  );
}
