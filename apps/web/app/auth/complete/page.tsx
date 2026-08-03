'use client';

import { useEffect } from 'react';

export default function AuthCompletePage() {
  useEffect(() => {
    const values = new URLSearchParams(window.location.hash.slice(1));
    const token = values.get('token');
    const next = values.get('next') || '/dashboard';
    if (!token) { window.location.replace('/login'); return; }
    localStorage.setItem('kall_token', token);
    window.location.replace(next);
  }, []);
  return <main className="shell"><section className="card" style={{ maxWidth: 520, margin: '70px auto' }}><h1>Signing you in…</h1><p>Finishing your secure Kall session.</p></section></main>;
}
