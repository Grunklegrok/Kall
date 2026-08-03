'use client';

import { useEffect, useState } from 'react';
import { decodeBase64Url, encodeBase64Url } from '../../lib/webauthn-bytes';

export default function SecuritySetupPage() {
  const [message, setMessage] = useState('');
  const [secret, setSecret] = useState('');
  const [uri, setUri] = useState('');
  const [code, setCode] = useState('');
  const [status, setStatus] = useState<{ totp_enabled: boolean; passkeys: { id: number; name: string }[] } | null>(null);

  function token() {
    const value = localStorage.getItem('kall_token');
    if (!value) { window.location.replace('/login'); throw new Error('Missing session'); }
    return value;
  }

  async function load() {
    const response = await fetch('/api/kall/auth/security', { headers: { Authorization: `Bearer ${token()}` } });
    if (response.status === 401) { localStorage.removeItem('kall_token'); window.location.replace('/login'); return; }
    if (response.ok) setStatus(await response.json());
  }

  useEffect(() => { void load(); }, []);

  async function beginTotp() {
    const response = await fetch('/api/kall/auth/totp/setup', { method: 'POST', headers: { Authorization: `Bearer ${token()}` } });
    const data = await response.json();
    if (!response.ok) { setMessage(data.detail || 'Unable to begin authenticator setup.'); return; }
    setSecret(data.secret); setUri(data.otpauth_uri); setMessage('Add this account to your authenticator app, then enter its six-digit code.');
  }

  async function verifyTotp() {
    const response = await fetch('/api/kall/auth/totp/verify', { method: 'POST', headers: { Authorization: `Bearer ${token()}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ code }) });
    const data = await response.json();
    setMessage(response.ok ? 'Authenticator-app 2FA is enabled.' : data.detail || 'The code was not accepted.');
    if (response.ok) { setSecret(''); setUri(''); setCode(''); await load(); }
  }

  async function addPasskey() {
    setMessage('Waiting for your device…');
    try {
      const response = await fetch('/api/kall/auth/passkeys/register/options', { method: 'POST', headers: { Authorization: `Bearer ${token()}` } });
      const options = await response.json();
      if (!response.ok) throw new Error(options.detail || 'Unable to start passkey setup.');
      const challenge = encodeBase64Url(decodeBase64Url(options.challenge));
      options.challenge = decodeBase64Url(options.challenge);
      options.user.id = decodeBase64Url(options.user.id);
      options.excludeCredentials = (options.excludeCredentials || []).map((item: { id: string }) => ({ ...item, id: decodeBase64Url(item.id) }));
      const created = await navigator.credentials.create({ publicKey: options }) as PublicKeyCredential | null;
      if (!created) throw new Error('Passkey creation was cancelled.');
      const attestation = created.response as AuthenticatorAttestationResponse;
      const credential = { id: created.id, rawId: encodeBase64Url(created.rawId), type: created.type, response: { attestationObject: encodeBase64Url(attestation.attestationObject), clientDataJSON: encodeBase64Url(attestation.clientDataJSON), transports: attestation.getTransports?.() || [] } };
      const complete = await fetch('/api/kall/auth/passkeys/register/complete', { method: 'POST', headers: { Authorization: `Bearer ${token()}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ challenge, credential, name: 'Primary passkey' }) });
      const data = await complete.json();
      if (!complete.ok) throw new Error(data.detail || 'Passkey registration failed.');
      setMessage('Your passkey is ready.'); await load();
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Passkey registration failed.'); }
  }

  return <main className="shell"><section className="hero" style={{ paddingBottom: 30 }}><span className="eyebrow">Account security</span><h1>Protect your Kall account.</h1><p>Add a passkey, authenticator-app 2FA, or both. You can return to this page later from Settings.</p></section>
    <div className="two">
      <section className="card"><h2>Passkey</h2><p>Use Face ID, Touch ID, Windows Hello, or a hardware security key.</p><p>{status?.passkeys.length || 0} passkey(s) registered</p><button className="button" onClick={addPasskey}>Create a passkey</button></section>
      <section className="card"><h2>Authenticator app</h2><p>{status?.totp_enabled ? 'Authenticator-app 2FA is enabled.' : 'Use a six-digit code from your preferred authenticator app.'}</p>{!secret && !status?.totp_enabled && <button className="button" onClick={beginTotp}>Set up authenticator</button>}{secret && <div className="form"><p><strong>Setup key:</strong> <code>{secret}</code></p><a href={uri}>Open in authenticator app</a><input className="input" value={code} onChange={(event) => setCode(event.target.value)} inputMode="numeric" placeholder="6-digit code" /><button className="button" onClick={verifyTotp}>Verify and enable</button></div>}</section>
    </div><p className="notice" aria-live="polite">{message}</p><div style={{ marginTop: 24 }}><a className="button secondary" href="/onboarding">Continue to onboarding</a></div></main>;
}
