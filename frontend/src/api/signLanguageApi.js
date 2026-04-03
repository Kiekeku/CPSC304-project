import { requestJson } from './http';

export async function analyzeVideo(file, modelId = null, options = {}) {
  const formData = new FormData();
  const headers = {};
  formData.append('file', file);

  if (modelId != null && modelId !== '') {
    formData.append('model_id', modelId);
  }

  if (options.userId != null && options.userId !== '') {
    headers['X-User-Id'] = String(options.userId);
  }

  return requestJson('/sign-language/analyze', {
    method: 'POST',
    headers,
    body: formData,
    signal: options.signal,
  });
}

export async function listVideoAnalyses() {
  return requestJson('/sign-language/analyses');
}

export async function getVideoAnalysis(analysisId) {
  return requestJson(`/sign-language/analyses/${analysisId}`);
}
