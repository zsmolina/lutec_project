import { Button } from '../ui/Button.jsx';
import { MaterialIcon } from '../ui/MaterialIcon.jsx';

function StatCard({ label, value, tone = 'default' }) {
  const toneClass = {
    default: 'text-on-surface',
    success: 'text-green-600',
    error: 'text-red-600',
    muted: 'text-on-surface-variant',
  }[tone];

  return (
    <div className="soft-card px-5 py-4">
      <p className="text-xs font-medium text-on-surface-variant">{label}</p>
      <p className={`mt-2 text-2xl font-bold tabular-nums ${toneClass}`}>{value}</p>
    </div>
  );
}

function statusLabel(status) {
  if (status === 'queued') return 'En cola';
  if (status === 'processing') return 'Procesando';
  return 'Iniciando';
}

export function BatchResultsPanel({
  jobStatus,
  isProcessing,
  isUploading,
  onDownloadExcel,
}) {
  const hasJob = Boolean(jobStatus);
  const jobState = jobStatus?.status;
  const isActive =
    isProcessing || (jobState && ['queued', 'processing'].includes(jobState));
  const progressPct =
    jobStatus?.total > 0 ? Math.round((jobStatus.processed / jobStatus.total) * 100) : 0;
  const hasCountableProgress = (jobStatus?.total ?? 0) > 0;
  const failures = jobStatus?.outcomes?.filter((item) => !item.success) ?? [];

  const currentFileLabel = isUploading
    ? 'Enviando lote al servidor…'
    : jobStatus?.current_file ??
      (jobState === 'queued'
        ? 'Validando archivos del ZIP…'
        : jobState === 'processing'
          ? 'Procesando facturas…'
          : 'Preparando lote…');

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-ises-green/15 text-ises-green">
            <MaterialIcon name="analytics" />
          </span>
          <div>
            <p className="text-sm font-bold text-on-surface">Resumen del lote</p>
            <p className="text-xs text-on-surface-variant">Progreso y descarga del consolidado</p>
          </div>
        </div>
        <Button
          variant="dark"
          size="md"
          icon="download"
          onClick={onDownloadExcel}
          disabled={!jobStatus?.download_ready}
          className="self-start sm:self-auto"
        >
          Descargar Excel
        </Button>
      </div>

      {!hasJob && !isProcessing && (
        <div className="soft-card-muted flex flex-col items-center px-6 py-14 text-center">
          <MaterialIcon name="inventory_2" className="mb-3 text-4xl text-on-surface-variant/40" />
          <p className="text-sm text-on-surface-variant">
            Los resultados aparecerán aquí cuando inicie la extracción.
          </p>
        </div>
      )}

      {isActive && (
        <div
          className="rounded-2xl border border-ises-green/25 bg-gradient-to-br from-ises-green/[0.08] via-white to-white p-8 shadow-soft"
          role="status"
          aria-live="polite"
          aria-busy="true"
        >
          <div className="flex flex-col items-center gap-4 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-ises-green/15">
              <MaterialIcon
                name="progress_activity"
                className="animate-spin text-5xl text-ises-green"
              />
            </div>
            <div className="space-y-2">
              <span className="inline-block rounded-full bg-ises-green/15 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-forest-green">
                {isUploading ? 'Enviando' : statusLabel(jobState)}
              </span>
              <p className="text-base font-bold text-on-surface">Procesando con IA</p>
              <p className="max-w-md text-sm text-on-surface-variant">{currentFileLabel}</p>
            </div>
          </div>

          <div className="mt-8">
            <div className="mb-2 flex justify-between text-xs font-medium text-on-surface-variant">
              <span>
                {hasCountableProgress
                  ? `${jobStatus.processed} de ${jobStatus.total} facturas`
                  : 'Contando facturas del ZIP…'}
              </span>
              <span className="font-semibold text-forest-green">
                {hasCountableProgress ? `${progressPct}%` : '—'}
              </span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-gray-200">
              {hasCountableProgress ? (
                <div
                  className="h-full rounded-full bg-ises-green transition-all duration-500 ease-out"
                  style={{ width: `${Math.max(progressPct, 2)}%` }}
                />
              ) : (
                <div className="progress-indeterminate h-full rounded-full bg-ises-green/80" />
              )}
            </div>
          </div>
        </div>
      )}

      {jobState === 'completed' && (
        <div className="space-y-6">
          <div className="flex items-center gap-3 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3">
            <MaterialIcon name="check_circle" className="text-2xl text-emerald-600" />
            <p className="text-sm font-semibold text-emerald-900">
              Lote finalizado — {jobStatus.succeeded} de {jobStatus.total} facturas procesadas
              correctamente
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Total" value={jobStatus.total} />
            <StatCard label="Exitosas" value={jobStatus.succeeded} tone="success" />
            <StatCard
              label="Fallidas"
              value={jobStatus.failed}
              tone={jobStatus.failed ? 'error' : 'muted'}
            />
            <StatCard label="Formato" value={jobStatus.format_label} tone="muted" />
          </div>

          {jobStatus.succeeded === 0 && (
            <div
              className="rounded-2xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-800"
              role="alert"
            >
              Ninguna factura se procesó correctamente. Revise el detalle de errores.
            </div>
          )}

          {failures.length > 0 && (
            <div className="soft-card p-4">
              <h4 className="mb-3 text-xs font-bold uppercase tracking-wider text-on-surface-variant">
                Facturas con error ({failures.length})
              </h4>
              <ul className="custom-scrollbar max-h-52 space-y-2 overflow-y-auto">
                {failures.map((item) => (
                  <li
                    key={item.filename}
                    className="rounded-xl border border-gray-100 bg-canvas-muted px-3 py-2.5 text-sm"
                  >
                    <p className="font-medium text-on-surface">{item.filename}</p>
                    {item.error && (
                      <p className="mt-1 text-xs leading-relaxed text-red-700">{item.error}</p>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {jobState === 'cancelled' && (
        <div
          className="rounded-2xl border border-amber-100 bg-amber-50 px-4 py-3 text-sm text-amber-900"
          role="alert"
        >
          {jobStatus.error ?? 'Procesamiento cancelado.'}
        </div>
      )}

      {jobState === 'failed' && (
        <div
          className="rounded-2xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-800"
          role="alert"
        >
          {jobStatus.error ?? 'El procesamiento del lote falló.'}
        </div>
      )}
    </div>
  );
}
