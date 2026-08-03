'use client';

import { useEffect, useState } from 'react';

const providers = [
  ['google', 'Google'],
  ['linkedin', 'LinkedIn'],
  ['github', 'GitHub'],
] as const;

export default function SocialAuthButtons() {
  const [available, setAvailable] = useState<Record<string, boolean>>({});

  useEffect(() => {
    fetch('/api/kall/auth/providers')
      .then((response) => response.json())
      .then(setAvailable)
      .catch(() => setAvailable({}));
  }, []);

  return (
    <div style={{ display: 'grid', gap: 10 }}>
      {providers.map(([key, label]) => (
        <a
          key={key}
          className="button secondary"
          href={`/api/kall/auth/oauth/${key}/start`}
          aria-disabled={available[key] === false}
          onClick={(event) => {
            if (available[key] === false) event.preventDefault();
          }}
          style={available[key] === false ? { opacity: 0.5, pointerEvents: 'none' } : undefined}
        >
          Continue with {label}
        </a>
      ))}
    </div>
  );
}
