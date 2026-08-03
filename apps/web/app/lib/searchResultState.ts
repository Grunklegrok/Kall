export type HiddenSearchResult = {
  url: string;
  title?: string;
  hiddenAt: string;
  reason: 'applied_external' | 'applied_kall';
};

declare global {
  interface WindowEventMap {
    'kall:search-results-changed': CustomEvent<void>;
  }
}

const HIDDEN_KEY = 'kall_hidden_search_results';
const PENDING_KEY = 'kall_pending_posting';

function normalize(url: string) {
  try {
    const parsed = new URL(url);
    parsed.hash = '';
    return parsed.toString();
  } catch {
    return url;
  }
}

export function getHiddenSearchResults(): HiddenSearchResult[] {
  if (typeof window === 'undefined') return [];
  try {
    const value = JSON.parse(localStorage.getItem(HIDDEN_KEY) || '[]');
    return Array.isArray(value) ? value : [];
  } catch {
    return [];
  }
}

export function isSearchResultHidden(url: string) {
  const target = normalize(url);
  return getHiddenSearchResults().some((item) => normalize(item.url) === target);
}

export function hideSearchResult(url: string, title: string | undefined, reason: HiddenSearchResult['reason']) {
  const target = normalize(url);
  const current = getHiddenSearchResults().filter((item) => normalize(item.url) !== target);
  current.push({ url: target, title, reason, hiddenAt: new Date().toISOString() });
  localStorage.setItem(HIDDEN_KEY, JSON.stringify(current));
  window.dispatchEvent(new CustomEvent<void>('kall:search-results-changed'));
}

export function restoreHiddenSearchResults() {
  localStorage.removeItem(HIDDEN_KEY);
  window.dispatchEvent(new CustomEvent<void>('kall:search-results-changed'));
}

export function hiddenSearchResultCount() {
  return getHiddenSearchResults().length;
}

export type PendingPosting = { url: string; title: string; snippet: string; profileId?: string };

export function setPendingPosting(posting: PendingPosting) {
  sessionStorage.setItem(PENDING_KEY, JSON.stringify(posting));
}

export function getPendingPosting(): PendingPosting | null {
  try {
    const value = JSON.parse(sessionStorage.getItem(PENDING_KEY) || 'null');
    return value && typeof value.url === 'string' ? value : null;
  } catch {
    return null;
  }
}

export function clearPendingPosting() {
  sessionStorage.removeItem(PENDING_KEY);
}
