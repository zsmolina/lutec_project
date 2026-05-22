export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

export const API_V1 = `${API_BASE_URL}/api/v1`;

export const DEFAULT_MAX_ZIP_MB = 100;
export const DEFAULT_MAX_ZIP_BYTES = DEFAULT_MAX_ZIP_MB * 1024 * 1024;

export const POLL_INTERVAL_PROCESSING_MS = 1000;
export const POLL_INTERVAL_QUEUED_MS = 1500;

export const AUTO_DOWNLOAD_STORAGE_KEY = 'lutec:autoDownloadExcel';
