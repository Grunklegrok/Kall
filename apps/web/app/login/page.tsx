'use client';

import { FormEvent, useState } from 'react';

export default function Login() {
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage('');
    setSubmitting(true);

    const form = new FormData(event.currentTarget);

    try {
      const response = await fetch('/api/kall/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: form.get('email'),
          password: form.get('password'),
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setMessage(data.detail || 'Login failed.');
        return;
      }

      localStorage.setItem('kall_token', data.access_token);
      window.location.assign('/dashboard');
    } catch {
      setMessage('Kall could not reach the API. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="shell">
      <div className="card" style={{ maxWidth: 520, margin: '70px auto' }}>
        <a className="brand" href="/" aria-label="Kall home">
          Kall
        </a>
        <h1>Welcome back</h1>
        <form className="form" onSubmit={submit}>
          <input className="input" name="email" type="email" placeholder="Email" required />
          <input className="input" name="password" type="password" placeholder="Password" required />
          <button className="button" type="submit" disabled={submitting}>
            {submitting ? 'Logging in…' : 'Log in'}
          </button>
        </form>
        <p aria-live="polite">{message}</p>
        <p>
          New to Kall? <a href="/register">Create an account</a>
        </p>
      </div>
    </main>
  );
}
