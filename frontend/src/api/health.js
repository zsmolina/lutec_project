import { apiGet } from './client.js';

export async function fetchHealth() {
  return apiGet('/health');
}
