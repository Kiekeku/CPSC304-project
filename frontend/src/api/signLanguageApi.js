import { requestJson } from './http';

export async function analyzeVideo(file) {
  const formData = new FormData();
  formData.append('file', file);

  return requestJson('/sign-language/analyze', {
    method: 'POST',
    body: formData,
  });
}
