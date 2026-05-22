import { useCallback, useState } from 'react';
import { consolidateFormapExcel } from '../api/formap.js';
import { useBackendHealth } from '../context/BackendHealthContext.jsx';
import {
  formatBytes,
  pickExcelFromFileList,
  validateFileSize,
} from '../utils/files.js';

export function useFormapConsolidation() {
  const { health, maxFormapExcelBytes } = useBackendHealth();
  const [excelFile, setExcelFile] = useState(null);
  const [rejectReason, setRejectReason] = useState(null);
  const [apiError, setApiError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastSuccessName, setLastSuccessName] = useState(null);

  const resetErrors = useCallback(() => {
    setRejectReason(null);
    setApiError(null);
  }, []);

  const onPickFile = useCallback(
    (fileList) => {
      resetErrors();
      setLastSuccessName(null);
      const file = pickExcelFromFileList(fileList);
      if (!file) {
        if (fileList?.length) {
          setRejectReason('Solo se aceptan archivos Excel (.xlsx o .xlsm).');
        }
        return;
      }
      const sizeError = validateFileSize(file, maxFormapExcelBytes, 'Excel');
      if (sizeError) {
        setRejectReason(sizeError);
        return;
      }
      setExcelFile(file);
    },
    [maxFormapExcelBytes, resetErrors],
  );

  const onClearFile = useCallback(() => {
    setExcelFile(null);
    setLastSuccessName(null);
    resetErrors();
  }, [resetErrors]);

  const startConsolidation = useCallback(async () => {
    if (!excelFile || isProcessing) return;
    if (health && health.status !== 'ok') {
      setApiError('El servidor no está disponible. Verifique que el backend esté en ejecución.');
      return;
    }

    setIsProcessing(true);
    setApiError(null);

    try {
      await consolidateFormapExcel(excelFile);
      setLastSuccessName(excelFile.name);
    } catch (err) {
      setApiError(err.message ?? 'No se pudo consolidar el archivo.');
    } finally {
      setIsProcessing(false);
    }
  }, [excelFile, isProcessing, health]);

  const maxLabel = formatBytes(maxFormapExcelBytes);

  return {
    excelFile,
    rejectReason,
    apiError,
    isProcessing,
    lastSuccessName,
    maxFormapExcelBytes,
    maxLabel,
    canProcess: Boolean(excelFile && !isProcessing && health?.status === 'ok'),
    onPickFile,
    onClearFile,
    startConsolidation,
  };
}
