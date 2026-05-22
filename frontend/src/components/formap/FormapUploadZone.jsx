import { useRef, useState } from 'react';
import { MaterialIcon } from '../ui/MaterialIcon.jsx';
import { Button } from '../ui/Button.jsx';
import { formatBytes } from '../../utils/files.js';

export function FormapUploadZone({
  file,
  onPickFile,
  onClearFile,
  disabled,
  maxBytes,
}) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const maxLabel = maxBytes ? formatBytes(maxBytes) : '50 MB';

  const openPicker = () => {
    if (!disabled) inputRef.current?.click();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (!disabled) onPickFile(e.dataTransfer.files);
  };

  if (file) {
    return (
      <div className="soft-card-muted flex flex-col items-center gap-5 p-6 sm:flex-row sm:text-left lg:p-8">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-700">
          <MaterialIcon name="table_chart" className="text-4xl" />
        </div>
        <div className="min-w-0 flex-1 text-center sm:text-left">
          <p className="text-xs font-semibold uppercase tracking-wider text-ises-green">
            Archivo Formap cargado
          </p>
          <p className="mt-1 break-all text-base font-bold text-on-surface" title={file.name}>
            {file.name}
          </p>
          <p className="mt-1 text-sm text-on-surface-variant">{formatBytes(file.size)}</p>
        </div>
        <Button variant="outline" size="md" onClick={onClearFile} disabled={disabled}>
          Cambiar archivo
        </Button>
      </div>
    );
  }

  return (
    <div
      role="button"
      tabIndex={disabled ? -1 : 0}
      onKeyDown={(e) => {
        if (disabled) return;
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openPicker();
        }
      }}
      onDragEnter={(e) => {
        e.preventDefault();
        if (!disabled) setIsDragging(true);
      }}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={openPicker}
      className={`flex min-h-[220px] cursor-pointer flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed p-8 text-center transition-colors duration-200 ${
        disabled
          ? 'cursor-not-allowed border-gray-200 bg-gray-50 opacity-50'
          : isDragging
            ? 'border-ises-green bg-ises-green/[0.06]'
            : 'border-gray-200 bg-canvas-muted/60 hover:border-ises-green/50 hover:bg-ises-green/[0.04]'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx,.xlsm,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        className="hidden"
        disabled={disabled}
        onChange={(e) => {
          onPickFile(e.target.files);
          e.target.value = '';
        }}
      />
      <div
        className={`flex h-16 w-16 items-center justify-center rounded-full transition-colors ${
          isDragging ? 'bg-ises-green text-white' : 'bg-white text-ises-green'
        }`}
      >
        <MaterialIcon name="upload_file" className="text-4xl" />
      </div>
      <div>
        <h3 className="text-base font-bold text-on-surface">Cargar Excel Formap</h3>
        <p className="mx-auto mt-2 max-w-md text-sm text-on-surface-variant">
          Arrastre el libro de auditoría con hojas GENERAL y componentes, o haga clic para
          seleccionarlo.
        </p>
      </div>
      <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-on-surface-variant ring-1 ring-gray-100">
        .xlsx / .xlsm · máximo {maxLabel}
      </span>
    </div>
  );
}
