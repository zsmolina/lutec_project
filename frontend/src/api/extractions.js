import { apiFetch, apiGet } from './client.js';

export async function fetchSupportedFormats() {
  const data = await apiGet('/formats');
  return data.formats ?? [];
}

export async function startBatchExtraction(zipFile, format) {
  const formData = new FormData();
  formData.append('file', zipFile, zipFile.name);
  formData.append('format', format);

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

function invoiceConsolidatedFilename(formatValue) {
  const yearLabel = (formatValue || 'facturas').replace(/_/g, '-');
  return `Facturas Consolidadas ${yearLabel}.xlsx`;
}

function parseAttachmentFilename(response, fallback) {
  const disposition = response.headers.get('Content-Disposition') ?? '';
  const match = disposition.match(/filename="?([^"]+)"?/i);
  return match?.[1] ?? fallback;
}

export async function downloadBatchExcel(jobId, formatValue) {
  const response = await apiFetch(`/extractions/jobs/${jobId}/download`);
  const blob = await response.blob();
  const filename = parseAttachmentFilename(
    response,
    invoiceConsolidatedFilename(formatValue),
  );

  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
