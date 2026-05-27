import { apiFetch, apiGet } from './client.js';

export async function fetchSupportedRetailers() {
  const data = await apiGet('/retailers');
  return data.retailers ?? [];
}

export async function fetchSupportedFormats(retailerId) {
  const query = retailerId ? `?retailer=${encodeURIComponent(retailerId)}` : '';
  const data = await apiGet(`/formats${query}`);
  return data.formats ?? [];
}

export async function startBatchExtraction(zipFile, retailerId) {
  const formData = new FormData();
  formData.append('retailer', retailerId);
  formData.append('file', zipFile, zipFile.name);

  const response = await apiFetch('/extractions/batch', {
    method: 'POST',
    body: formData,
  });
  return response.json();
}

export async function fetchJobStatus(jobId) {
  return apiGet(`/extractions/jobs/${jobId}`);
}

export async function cancelBatchJob(jobId) {
  const response = await apiFetch(`/extractions/jobs/${jobId}`, { method: 'DELETE' });
  return response.json();
}

function parseAttachmentFilename(response, fallback) {
  const disposition = response.headers.get('Content-Disposition') ?? '';
  const match = disposition.match(/filename="?([^"]+)"?/i);
  return match?.[1] ?? fallback;
}

export async function downloadBatchExcel(jobId, retailerId, formatValue) {
  const response = await apiFetch(`/extractions/jobs/${jobId}/download`);
  const blob = await response.blob();
  const retailerLabel =
    retailerId === 'afinia' ? 'Afinia' : retailerId === 'aire' ? 'Air-e' : 'Facturas';
  const fallback =
    !formatValue || formatValue === 'auto'
      ? `Facturas ${retailerLabel} Consolidadas.xlsx`
      : `Facturas ${retailerLabel} Consolidadas ${formatValue.replace(/_/g, '-')}.xlsx`;
  const filename = parseAttachmentFilename(response, fallback);

  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
