import { Button } from '../ui/Button.jsx';

export function ProcessActionBar({
  readyHint,
  canProcess,
  processBlockReason,
  isProcessing,
  autoDownload,
  onAutoDownloadChange,
  onStart,
  onCancel,
  showCancel,
}) {
  return (
    <div className="soft-card p-6 lg:p-8">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-xl space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wider text-ises-green">
            Listo para procesar
          </p>
          <p className="text-sm leading-relaxed text-on-surface-variant">{readyHint}</p>
          {processBlockReason && (
            <p className="text-sm font-medium text-amber-800">{processBlockReason}</p>
          )}
          <label className="inline-flex cursor-pointer items-center gap-2.5 text-sm text-on-surface-variant">
            <input
              type="checkbox"
              checked={autoDownload}
              onChange={(e) => onAutoDownloadChange(e.target.checked)}
              disabled={isProcessing}
              className="rounded border-outline text-ises-green focus:ring-ises-green/30"
            />
            Descargar Excel automáticamente al finalizar
          </label>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {showCancel && (
            <Button variant="secondary" size="lg" onClick={onCancel}>
              Cancelar
            </Button>
          )}
          <Button
            variant="primary"
            size="lg"
            onClick={onStart}
            disabled={!canProcess}
            icon={isProcessing ? 'progress_activity' : 'auto_awesome'}
            iconSpin={isProcessing}
            className="min-w-[220px]"
          >
            {isProcessing ? 'Procesando lote…' : 'Iniciar extracción IA'}
          </Button>
        </div>
      </div>
    </div>
  );
}
