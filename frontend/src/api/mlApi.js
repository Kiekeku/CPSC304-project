import { requestJson } from './http';

const BASE = '/ml';

export async function predict(features = {}, metadata = {}) {
  return requestJson(`${BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ features, metadata })
  });
}

export async function createDataset(name) {
  return requestJson(`${BASE}/datasets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  });
}

export async function listDatasets() {
  return requestJson(`${BASE}/datasets`);
}

export async function getDataset(datasetId) {
  return requestJson(`${BASE}/datasets/${datasetId}`);
}

export async function addGestureLabel(datasetId, label, options = {}) {
  const headers = { 'Content-Type': 'application/json' };

  if (options.userId != null && options.userId !== '') {
    headers['X-User-Id'] = String(options.userId);
  }

  return requestJson(`${BASE}/datasets/${datasetId}/gestures`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ label })
  });
}

export async function uploadGestureVideo(datasetId, label, file) {
  const formData = new FormData();
  formData.append('file', file);

  return requestJson(`${BASE}/datasets/${datasetId}/gestures/${encodeURIComponent(label)}/videos`, {
    method: 'POST',
    body: formData
  });
}

export async function trainDataset(datasetId) {
  return requestJson(`${BASE}/datasets/${datasetId}/train`, { method: 'POST' });
}

export async function recognizeGesture(datasetId, landmarks) {
  return requestJson(`${BASE}/datasets/${datasetId}/recognize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ landmarks })
  });
}

export async function recognizeGestureFrame(datasetId, file) {
  const formData = new FormData();
  formData.append('file', file);

  return requestJson(`${BASE}/datasets/${datasetId}/recognize-frame`, {
    method: 'POST',
    body: formData
  });
}
