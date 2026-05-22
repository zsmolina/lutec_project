import { API_V1, parseApiError } from './client.js';

export async function consolidateFormapExcel(excelFile) {
  const formData = new FormData();
  formData.append('file', excelFile, excelFile.name);

  const response = await fetch(`${API_V1}/formap/consolidate`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition') ?? '';
  const match = disposition.match(/filename="?([^"]+)"?/i);
  const filename = match?.[1] ?? 'Informe Formap.xlsx';

  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
