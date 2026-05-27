import { useCallback, useEffect, useRef, useState } from 'react';
import {
  cancelBatchJob,
  downloadBatchExcel,
  fetchJobStatus,
  startBatchExtraction,
} from '../api/extractions.js';
import { useBackendHealth } from '../context/BackendHealthContext.jsx';
import {
  AUTO_DOWNLOAD_STORAGE_KEY,
  POLL_INTERVAL_PROCESSING_MS,
  POLL_INTERVAL_QUEUED_MS,
} from '../config/api.js';
import { DEFAULT_RETAILER_ID, RETAILERS } from '../constants/retailers.js';
import { pickZipFromFileList, validateZipFileSize } from '../utils/files.js';

const TERMINAL_STATUSES = new Set(['completed', 'failed', 'cancelled']);

function sleep(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function readAutoDownloadPreference() {
  return localStorage.getItem(AUTO_DOWNLOAD_STORAGE_KEY) === 'true';
}

export function useBatchExtraction() {
  const [retailerId, setRetailerId] = useState(DEFAULT_RETAILER_ID);
  const [zipFile, setZipFile] = useState(null);
  const [rejectReason, setRejectReason] = useState(null);
  const [apiError, setApiError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [activeJobId, setActiveJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const { health, maxZipBytes } = useBackendHealth();
  const [autoDownload, setAutoDownload] = useState(readAutoDownloadPreference);
  const pollRunIdRef = useRef(0);

  const retailerOptions = RETAILERS;

  const resetErrors = useCallback(() => {
    setRejectReason(null);
    setApiError(null);
  }, []);

  const onRetailerChange = useCallback(
    (id) => {
      setRetailerId(id);
      setApiError(null);
      setJobStatus(null);
      setActiveJobId(null);
    },
    [],
  );

  const onPickFile = useCallback(
    (fileList) => {
      resetErrors();
      setJobStatus(null);
      setActiveJobId(null);
      const zip = pickZipFromFileList(fileList);
      if (!zip) {
        if (fileList?.length) {
          setRejectReason('Solo se acepta un archivo ZIP con facturas PDF en su interior.');
        }
        return;
      }
      const sizeError = validateZipFileSize(zip, maxZipBytes);
      if (sizeError) {
        setRejectReason(sizeError);
        return;
      }
      setZipFile(zip);
    },
    [maxZipBytes, resetErrors],
  );

  const onClearFile = useCallback(() => {
    setZipFile(null);
    setJobStatus(null);
    setActiveJobId(null);
    resetErrors();
  }, [resetErrors]);

  const onAutoDownloadChange = useCallback((enabled) => {
    setAutoDownload(enabled);
    localStorage.setItem(AUTO_DOWNLOAD_STORAGE_KEY, enabled ? 'true' : 'false');
  }, []);

  const downloadExcel = useCallback(async () => {
    if (!jobStatus?.job_id || !jobStatus.download_ready) return;
    try {
      await downloadBatchExcel(
        jobStatus.job_id,
        jobStatus.retailer,
        jobStatus.format,
      );
    } catch (err) {
      setApiError(err.message ?? 'No se pudo descargar el Excel.');
    }
  }, [jobStatus]);

  useEffect(() => {
    if (!activeJobId || !isProcessing) return undefined;

    const runId = ++pollRunIdRef.current;
    let cancelled = false;

    const poll = async () => {
      let delayMs = 0;

      while (!cancelled && pollRunIdRef.current === runId) {
        if (delayMs > 0) {
          await sleep(delayMs);
        }
        if (cancelled || pollRunIdRef.current !== runId) return;

        try {
          const status = await fetchJobStatus(activeJobId);
          if (cancelled || pollRunIdRef.current !== runId) return;

          setJobStatus(status);

          if (TERMINAL_STATUSES.has(status.status)) {
            setIsProcessing(false);
            setIsUploading(false);
            setActiveJobId(null);

            if (status.status === 'failed' && status.error) {
              setApiError(status.error);
            }
            if (status.status === 'cancelled' && status.error) {
              setApiError(status.error);
            }
            if (status.download_ready && autoDownload) {
              try {
                await downloadBatchExcel(activeJobId, status.retailer, status.format);
              } catch (err) {
                setApiError(err.message ?? 'No se pudo descargar el Excel.');
              }
            }
            return;
          }

          delayMs =
            status.status === 'processing'
              ? POLL_INTERVAL_PROCESSING_MS
              : POLL_INTERVAL_QUEUED_MS;
        } catch (err) {
          if (cancelled || pollRunIdRef.current !== runId) return;
          setIsProcessing(false);
          setIsUploading(false);
          setActiveJobId(null);
          setApiError(err.message ?? 'Error al consultar el estado del procesamiento.');
          return;
        }
      }
    };

    poll();

    return () => {
      cancelled = true;
    };
  }, [activeJobId, isProcessing, autoDownload]);

  const startProcessing = useCallback(async () => {
    if (!zipFile || !retailerId || isProcessing) return;
    if (health && !health.openai_configured) {
      setApiError('OpenAI no está configurado en el servidor. Revise backend/.env');
      return;
    }

    pollRunIdRef.current += 1;
    setIsProcessing(true);
    setIsUploading(true);
    setApiError(null);
    setJobStatus({
      status: 'queued',
      total: 0,
      processed: 0,
      current_file: 'Enviando lote al servidor…',
    });
    setActiveJobId(null);

    try {
      const created = await startBatchExtraction(zipFile, retailerId);
      setIsUploading(false);
      setJobStatus(created);
      setActiveJobId(created.job_id);
    } catch (err) {
      setIsProcessing(false);
      setIsUploading(false);
      setActiveJobId(null);
      setJobStatus(null);
      setApiError(
        err.message ??
          'No se pudo iniciar el procesamiento. Verifique que el backend esté en ejecución.',
      );
    }
  }, [zipFile, retailerId, isProcessing, health]);

  const cancelProcessing = useCallback(async () => {
    const jobId = activeJobId ?? jobStatus?.job_id;
    if (!jobId) return;

    pollRunIdRef.current += 1;
    try {
      const status = await cancelBatchJob(jobId);
      setJobStatus(status);
      setIsProcessing(false);
      setIsUploading(false);
      setActiveJobId(null);
      if (status.error) setApiError(status.error);
    } catch (err) {
      setApiError(err.message ?? 'No se pudo cancelar el procesamiento.');
    }
  }, [activeJobId, jobStatus]);

  const selectedRetailer = retailerOptions.find((r) => r.id === retailerId);

  const processBlockReason = (() => {
    if (isProcessing) return null;
    if (!retailerId) return 'Seleccione el comercializador de las facturas.';
    if (!zipFile) return 'Suba un archivo ZIP con las facturas en PDF.';
    if (health?.status === 'unreachable') {
      return 'No se puede contactar el backend. Ejecute el servidor (puerto 8000) y recargue la página.';
    }
    if (health?.status === 'ok' && !health.openai_configured) {
      return 'OpenAI no está configurado. Revise OPENAI_API_KEY en backend/.env';
    }
    return null;
  })();

  const canProcess = Boolean(
    retailerId && zipFile && !isProcessing && !processBlockReason,
  );

  return {
    retailerId,
    retailerOptions,
    selectedRetailer,
    zipFile,
    rejectReason,
    apiError,
    isProcessing,
    isUploading,
    jobStatus,
    maxZipBytes,
    autoDownload,
    canProcess,
    processBlockReason,
    onRetailerChange,
    onPickFile,
    onClearFile,
    onAutoDownloadChange,
    startProcessing,
    cancelProcessing,
    downloadExcel,
  };
}
