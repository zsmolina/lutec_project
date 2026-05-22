import { MaterialIcon } from '../ui/MaterialIcon.jsx';

export function AppHeader({ title = 'Extracción de facturas', subtitle }) {
  return (
    <header className="z-30 shrink-0 border-b border-gray-100 bg-white">
      <div className="flex min-h-[72px] flex-wrap items-center justify-between gap-4 px-6 py-4 lg:px-8">
        <div className="min-w-0">
          <h2 className="font-display text-xl font-bold tracking-tight text-ises-green lg:text-2xl">
            {title}
          </h2>
          {subtitle && (
            <p className="mt-0.5 hidden text-sm text-on-surface-variant sm:block">{subtitle}</p>
          )}
        </div>

        <div className="flex items-center gap-3">
          <label className="relative hidden md:block">
            <span className="sr-only">Buscar</span>
            <MaterialIcon
              name="search"
              className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[20px] text-on-surface-variant"
            />
            <input
              type="search"
              placeholder="Buscar módulos…"
              disabled
              className="input-soft w-56 cursor-default rounded-full pl-10 opacity-80 lg:w-64"
            />
          </label>
          <button
            type="button"
            className="flex h-10 w-10 items-center justify-center rounded-full border border-gray-100 bg-canvas-muted text-on-surface-variant transition-colors hover:bg-gray-100"
            aria-label="Notificaciones"
          >
            <MaterialIcon name="notifications" className="text-[22px]" />
          </button>
        </div>
      </div>
    </header>
  );
}
