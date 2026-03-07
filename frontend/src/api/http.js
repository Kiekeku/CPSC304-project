export async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const isJson = response.headers.get('content-type')?.includes('application/json');
  const body = isJson ? await response.json() : null;
  return { ok: response.ok, status: response.status, body };
}

export async function requestText(url, options = {}) {
  const response = await fetch(url, options);
  const text = await response.text();
  return { ok: response.ok, status: response.status, text };
}
