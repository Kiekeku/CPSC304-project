import { requestJson } from './http';

export async function analyzeVideo(file, modelId = null) {
  const formData = new FormData();
  formData.append('file', file);

  if (modelId != null && modelId !== '') {
    formData.append('model_id', modelId);
  }

  return requestJson('/sign-language/analyze', {
    method: 'POST',
    body: formData,
  });
}

export async function listVideoAnalyses() {
  return requestJson('/sign-language/analyses');
}

export async function getVideoAnalysis(analysisId) {
  return requestJson(`/sign-language/analyses/${analysisId}`);
}
