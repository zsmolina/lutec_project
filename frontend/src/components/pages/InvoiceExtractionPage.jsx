import { useEffect, useRef } from 'react';
import { UploadZone } from '../extraction/UploadZone.jsx';
import { RetailerSelector } from '../extraction/RetailerSelector.jsx';
import { BatchResultsPanel } from '../extraction/BatchResultsPanel.jsx';
import { ProcessActionBar } from '../extraction/ProcessActionBar.jsx';
import { PageStep } from '../ui/PageStep.jsx';
import { MaterialIcon } from '../ui/MaterialIcon.jsx';
import { useBatchExtraction } from '../../hooks/useBatchExtraction.js';

const WORKFLOW_STEPS = [
  { n: 1, label: 'Comercializador', icon: 'business' },
  { n: 2, label: 'ZIP', icon: 'folder_zip' },
  { n: 3, label: 'Procesar', icon: 'auto_awesome' },
  { n: 4, label: 'Excel', icon: 'table_chart' },
];

function AlertBanner({ message }) {
  if (!message) return null;
  return (
    <div
      className="flex items-start gap-3 rounded-2xl border border-red-100 bg-red-50 px-5 py-4 text-sm text-red-800"
      role="alert"
    >
      <MaterialIcon name="error" className="shrink-0 text-[22px]" />
      <span>{message}</span>
    </div>
  );
}

function WorkflowStrip() {
  return (
    <div className="soft-card p-5 lg:p-6">
      <p className="mb-4 text-xs font-semibold uppercase tracking-wider text-on-surface-variant">
        Flujo de trabajo
      </p>
      <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {WORKFLOW_STEPS.map((s) => (
          <li
            key={s.n}
            className="flex items-center gap-3 rounded-2xl bg-canvas-muted px-4 py-3 transition-colors hover:bg-ises-green/8"
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white text-ises-green ring-1 ring-gray-100">
              <MaterialIcon name={s.icon} className="text-[20px]" />
            </span>
            <div>
              <p className="text-[10px] font-semibold text-on-surface-variant">Paso {s.n}</p>
              <p className="text-sm font-semibold text-on-surface">{s.label}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

export function InvoiceExtractionPage() {
  const {
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
  } = useBatchExtraction();

  const isJobActive =
    isProcessing || (jobStatus && ['queued', 'processing'].includes(jobStatus.status));

  const resultsRef = useRef(null);

  useEffect(() => {
    if (isJobActive && resultsRef.current) {
      resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [isJobActive]);

  const readyHint =
    zipFile && selectedRetailer
      ? `Lote ${selectedRetailer.label}: el año de cada factura se detecta automáticamente.`
      : !retailerId
        ? 'Seleccione Air-e o Afinia según el comercializador de las facturas.'
        : 'Suba un archivo ZIP con las facturas en PDF.';

  return (
    <main className="app-main-bg custom-scrollbar flex-1 overflow-y-auto">
      <div className="mx-auto flex max-w-[1180px] flex-col gap-6 px-6 py-6 lg:gap-7 lg:px-8 lg:py-8">
        <p className="text-sm text-on-surface-variant sm:hidden">
          Elija comercializador, cargue un ZIP y obtenga el consolidado Excel con detección automática
          de formato.
        </p>

        <WorkflowStrip />
        <AlertBanner message={rejectReason || apiError} />

        <PageStep
          step="1"
          title="Comercializador"
          description="Indique si las facturas del lote corresponden a Air-e o Afinia. El motor aplicará las reglas y plantillas correctas."
        >
          <RetailerSelector
            options={retailerOptions}
            value={retailerId}
            onChange={onRetailerChange}
            disabled={isProcessing}
          />
        </PageStep>

        <PageStep
          step="2"
          title="Cargar lote ZIP"
          description={
            retailerId === 'afinia'
              ? 'ZIP con PDFs Afinia. 2024 = 1 hoja; 2025/2026 = 2 hojas. Puede mezclar años.'
              : 'ZIP con PDFs Air-e (2023, 2024 o 2025/2026). Puede mezclar años en el mismo lote.'
          }
        >
          <UploadZone
            file={zipFile}
            onPickFile={onPickFile}
            onClearFile={onClearFile}
            disabled={isProcessing}
            maxZipBytes={maxZipBytes}
          />
        </PageStep>

        <ProcessActionBar
          readyHint={readyHint}
          canProcess={canProcess}
          processBlockReason={processBlockReason}
          isProcessing={isProcessing}
          autoDownload={autoDownload}
          onAutoDownloadChange={onAutoDownloadChange}
          onStart={startProcessing}
          onCancel={cancelProcessing}
          showCancel={Boolean(isJobActive && jobStatus?.job_id)}
        />

        <PageStep
          step="3"
          title="Resultados"
          description="Progreso, clasificación por factura y descarga del Excel consolidado."
          className="scroll-mt-6"
        >
          <div ref={resultsRef}>
            <BatchResultsPanel
              jobStatus={jobStatus}
              isProcessing={isProcessing}
              isUploading={isUploading}
              onDownloadExcel={downloadExcel}
            />
          </div>
        </PageStep>
      </div>
    </main>
  );
}
