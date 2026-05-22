import { MaterialIcon } from '../ui/MaterialIcon.jsx';
import { APP_MODULES, MODULE_ORDER } from '../../constants/modules.js';

function SidebarLink({ iconName, label, active, disabled, onClick }) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`group flex w-full items-center gap-3 rounded-2xl px-3 py-2.5 text-left transition-colors duration-200 ${
        active
          ? 'bg-ises-green/12'
          : disabled
            ? 'cursor-default opacity-80'
            : 'hover:bg-canvas-muted'
      }`}
    >
      <span
        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full transition-colors duration-200 ${
          active
            ? 'bg-ises-green text-white'
            : 'bg-gray-100 text-on-surface-variant group-hover:bg-gray-200/80'
        }`}
      >
        <MaterialIcon name={iconName} className="text-[20px]" />
      </span>
      <span className="flex min-w-0 flex-1 flex-col gap-0.5">
        <span
          className={`text-[13px] font-medium leading-snug ${
            active ? 'text-on-surface' : 'text-on-surface-variant'
          }`}
        >
          {label}
        </span>
        {disabled && (
          <span className="w-fit text-[10px] font-medium text-on-surface-variant/80">Pronto</span>
        )}
      </span>
    </button>
  );
}

export function Sidebar({ activeModuleId, onModuleChange }) {
  return (
    <aside className="z-40 flex h-full w-[272px] shrink-0 flex-col border-r border-gray-100 bg-white">
      <div className="flex shrink-0 items-center gap-3 px-5 py-6">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-ises-green text-white">
          <MaterialIcon name="token" className="text-[22px]" />
        </div>
        <div className="min-w-0">
          <h1 className="font-display text-lg font-bold text-on-surface">Lutec</h1>
          <p className="text-[10px] font-semibold uppercase tracking-widest text-on-surface-variant">
            by ISES
          </p>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto px-4 py-2 custom-scrollbar">
        <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-on-surface-variant/70">
          Módulos
        </p>
        {MODULE_ORDER.map((moduleId) => {
          const item = APP_MODULES[moduleId];
          const isActive = activeModuleId === moduleId;
          return (
            <SidebarLink
              key={moduleId}
              iconName={item.icon}
              label={item.label}
              active={isActive}
              disabled={!item.enabled}
              onClick={() => item.enabled && onModuleChange(moduleId)}
            />
          );
        })}
      </nav>

      <div className="mt-auto shrink-0 border-t border-gray-100 p-4">
        <div className="flex items-center gap-3 rounded-2xl bg-canvas-muted px-3 py-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white text-on-surface-variant">
            <MaterialIcon name="account_circle" className="text-[22px]" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold text-on-surface">Admin ISES</p>
            <p className="text-xs text-on-surface-variant">Enterprise Account</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
