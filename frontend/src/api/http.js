const AUTH_STORAGE_KEY = 'team107.currentUser';

function resolveStoredUserId() {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) {
      return null;
    }

    const parsed = JSON.parse(raw);
    return parsed?.userId != null && parsed.userId !== '' ? String(parsed.userId) : null;
  } catch {
    return null;
  }
}

function withAuthHeaders(options = {}) {
  const headers = new Headers(options.headers || {});
  const explicitUserId = options.userId != null && options.userId !== '' ? String(options.userId) : null;
  const storedUserId = resolveStoredUserId();
  const userId = explicitUserId || storedUserId;

  if (userId && !headers.has('X-User-Id')) {
    headers.set('X-User-Id', userId);
  }

  return {
    ...options,
    headers,
  };
}

export async function requestJson(url, options = {}) {
  const response = await fetch(url, withAuthHeaders(options));
  const isJson = response.headers.get('content-type')?.includes('application/json');
  const body = isJson ? await response.json() : null;
  return { ok: response.ok, status: response.status, body };
}

export async function requestText(url, options = {}) {
  const response = await fetch(url, withAuthHeaders(options));
  const text = await response.text();
  return { ok: response.ok, status: response.status, text };
}
