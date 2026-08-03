'use client';

import { useEffect, useState } from 'react';

type ToastKind = 'error' | 'success' | 'info';
type ToastDetail = { message: string; kind?: ToastKind; duration?: number };
type ToastItem = ToastDetail & { id: number };

declare global { interface WindowEventMap { 'kall:toast': CustomEvent<ToastDetail>; } }

export function showToast(message: string, kind: ToastKind = 'info', duration = 4200) {
  if (typeof window === 'undefined') return;
  window.dispatchEvent(new CustomEvent<ToastDetail>('kall:toast', { detail: { message, kind, duration } }));
}

export default function ToastHost() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  useEffect(() => {
    let nextId = 0;
    const add = (detail: ToastDetail) => {
      const message = String(detail.message || '').trim();
      if (!message) return;
      const id = ++nextId;
      const duration = detail.duration ?? 4200;
      setToasts((current) => [...current.slice(-2), { ...detail, message, id }]);
      window.setTimeout(() => setToasts((current) => current.filter((toast) => toast.id !== id)), duration);
    };
    const onToast = (event: CustomEvent<ToastDetail>) => add(event.detail);
    const onError = (event: ErrorEvent) => add({ message: event.message || 'An unexpected error occurred.', kind: 'error' });
    const onRejection = (event: PromiseRejectionEvent) => add({ message: event.reason instanceof Error ? event.reason.message : 'An unexpected request error occurred.', kind: 'error' });
    window.addEventListener('kall:toast', onToast);
    window.addEventListener('error', onError);
    window.addEventListener('unhandledrejection', onRejection);
    return () => {
      window.removeEventListener('kall:toast', onToast);
      window.removeEventListener('error', onError);
      window.removeEventListener('unhandledrejection', onRejection);
    };
  }, []);
  if (!toasts.length) return null;
  return <div className="kall-toast-region" role="region" aria-label="Notifications" aria-live="polite">{toasts.map((toast) => <div className={`kall-toast kall-toast-${toast.kind || 'info'}`} role={toast.kind === 'error' ? 'alert' : 'status'} key={toast.id}><span>{toast.message}</span><button type="button" aria-label="Dismiss notification" onClick={() => setToasts((current) => current.filter((item) => item.id !== toast.id))}>×</button></div>)}</div>;
}
