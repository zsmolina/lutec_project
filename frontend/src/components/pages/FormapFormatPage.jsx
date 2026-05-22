import { FormapUploadZone } from '../formap/FormapUploadZone.jsx';
import { PageStep } from '../ui/PageStep.jsx';
import { Button } from '../ui/Button.jsx';
import { MaterialIcon } from '../ui/MaterialIcon.jsx';
import { useFormapConsolidation } from '../../hooks/useFormapConsolidation.js';

function AlertBanner({ message, variant = 'error' }) {
  if (!message) return null;
  const styles =
    variant === 'success'
      ? 'border-emerald-100 bg-emerald-50 text-emerald-800'
      : 'border-red-100 bg-red-50 text-red-800';
  const icon = variant === 'success' ? 'check_circle' : 'error';

  return (
    <div className={`flex items-start gap-3 rounded-2xl border px-5 py-4 text-sm ${styles}`} role="alert">
      <MaterialIcon name={icon} className="shrink-0 text-[22px]" />
      <span>{message}</span>
    </div>
  );
}

export function FormapFormatPage() {
  const {
    excelFile,
    rejectReason,
    apiError,
    isProcessing,
    lastSuccessName,
    maxFormapExcelBytes,
    maxLabel,
    canProcess,
    onPickFile,
    onClearFile,
    startConsolidation,
  } = useFormapConsolidation();

  const readyHint = excelFile
    ? `Archivo listo: ${excelFile.name}. Se generará un informe unificado en una sola hoja.`
    : 'Seleccione el Excel de entrada con el esquema Formap.';

  return (
    <main className="app-main-bg custom-scrollbar flex-1 overflow-y-auto">
      <div className="mx-auto flex max-w-[1180px] flex-col gap-6 px-6 py-6 lg:gap-7 lg:px-8 lg:py-8">
        <AlertBanner message={rejectReason || apiError} />
        {lastSuccessName && !apiError && !isProcessing && (
          <AlertBanner
            variant="success"
            message={`Informe generado correctamente a partir de «${lastSuccessName}». Revise su carpeta de descargas.`}
          />
        )}

        <PageStep
          step="1"
          title="Archivo de entrada"
          description="Libro Excel exportado desde el esquema Formap, con hoja GENERAL y hojas de componentes."
        >
          <FormapUploadZone
            file={excelFile}
            onPickFile={onPickFile}
            onClearFile={onClearFile}
            disabled={isProcessing}
            maxBytes={maxFormapExcelBytes}
          />
        </PageStep>

        <div className="soft-card p-6 lg:p-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-xl space-y-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-ises-green">
                Generar informe
              </p>
              <p className="text-sm leading-relaxed text-on-surface-variant">{readyHint}</p>
              <p className="text-xs text-on-surface-variant/80">Tamaño máximo: {maxLabel}</p>
            </div>
            <Button
              variant="primary"
              size="lg"
              onClick={startConsolidation}
              disabled={!canProcess}
              icon={isProcessing ? 'progress_activity' : 'transform'}
              iconSpin={isProcessing}
              className="min-w-[240px]"
            >
              {isProcessing ? 'Consolidando…' : 'Consolidar y descargar Excel'}
            </Button>
          </div>
        </div>
      </div>
    </main>
  );
}
