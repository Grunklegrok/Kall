'use client';

import { FormEvent, useState } from 'react';

type AuthResponse = {
  access_token: string;
};

export default function Register() {
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage('');
    setSubmitting(true);

    const form = new FormData(event.currentTarget);
    const password = String(form.get('password') || '');
    const confirmation = String(form.get('password_confirmation') || '');

    if (password !== confirmation) {
      setMessage('Passwords do not match.');
      setSubmitting(false);
      return;
    }

    try {
      const response = await fetch('/api/kall/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: form.get('full_name'),
          email: form.get('email'),
          password,
          country: form.get('country') || null,
          state_region: form.get('state_region') || null,
        }),
      });

      const data = (await response.json()) as AuthResponse & { detail?: string | unknown[] };
      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => JSON.stringify(item)).join(', ')
          : data.detail;
        setMessage(typeof detail === 'string' ? detail : 'Account creation failed.');
        return;
      }

      localStorage.setItem('kall_token', data.access_token);
      window.location.assign('/onboarding');
    } catch {
      setMessage('Kall could not reach the API. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="shell">
      <div className="card" style={{ maxWidth: 560, margin: '70px auto' }}>
        <a className="brand" href="/" aria-label="Kall home">
          Kall
        </a>
        <h1>Create your account</h1>
        <p>Start your private career workspace, then build your Kall profile.</p>
        <form className="form" onSubmit={submit}>
          <input className="input" name="full_name" placeholder="Full name" required />
          <input className="input" name="email" type="email" placeholder="Email" required />
          <input
            className="input"
            name="password"
            type="password"
            placeholder="Password (at least 10 characters)"
            minLength={10}
            required
          />
          <input
            className="input"
            name="password_confirmation"
            type="password"
            placeholder="Confirm password"
            minLength={10}
            required
          />
          <input className="input" name="country" placeholder="Country (optional)" />
          <input className="input" name="state_region" placeholder="State or region (optional)" />
          <button className="button" type="submit" disabled={submitting}>
            {submitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>
        <p aria-live="polite">{message}</p>
        <p>
          Already have an account? <a href="/login">Log in</a>
        </p>
      </div>
    </main>
  );
}
