import { requestJson } from './http';

export async function predict(features = {}, metadata = {}) {
  return requestJson('/ml/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ features, metadata })
  });
}
