import { API_V1 } from '../config/api.js';

export { API_V1 };

export async function parseApiError(response) {
  let detail = `Error del servidor (${response.status})`;
  try {
    const body = await response.json();
    if (body.detail) {
      detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
    }
  } catch {
    /* sin cuerpo JSON */
  }
  return detail;
}

export async function apiGet(path) {
  const response = await fetch(`${API_V1}${path}`);
  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }
  return response.json();
}

export async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_V1}${path}`, options);
  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }
  return response;
}
