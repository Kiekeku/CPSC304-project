import { requestJson } from './http';

export async function analyzeVideo(file) {
  const formData = new FormData();
  formData.append('file', file);

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
