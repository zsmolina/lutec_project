const ZIP_MIME_TYPES = new Set([
  'application/zip',
  'application/x-zip-compressed',
  'multipart/x-zip',
]);

export function isZipFile(file) {
  if (!file) return false;
  return ZIP_MIME_TYPES.has(file.type) || file.name?.toLowerCase().endsWith('.zip');
}

export function pickZipFromFileList(fileList) {
  if (!fileList?.length) return null;
  const file = fileList[0];
  return isZipFile(file) ? file : null;
}

export function validateZipFileSize(file, maxBytes) {
  return validateFileSize(file, maxBytes, 'ZIP');
}

const EXCEL_EXTENSIONS = ['.xlsx', '.xlsm'];

export function isExcelFile(file) {
  if (!file) return false;
  const name = file.name?.toLowerCase() ?? '';
  return EXCEL_EXTENSIONS.some((ext) => name.endsWith(ext));
}

export function pickExcelFromFileList(fileList) {
  if (!fileList?.length) return null;
  const file = fileList[0];
  return isExcelFile(file) ? file : null;
}

export function validateFileSize(file, maxBytes, label = 'archivo') {
  if (!file || !maxBytes) return null;
  if (file.size > maxBytes) {
    const maxMb = Math.round(maxBytes / (1024 * 1024));
    return `El ${label} supera el tamaño máximo permitido (${maxMb} MB).`;
  }
  return null;
}

export function formatBytes(bytes) {
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
