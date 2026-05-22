import { MaterialIcon } from '../ui/MaterialIcon.jsx';

export function FormatSelector({ options, value, onChange, disabled }) {
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {options.map((option) => {
        const selected = value === option.id;
        return (
          <label
            key={option.id}
            className={`relative flex cursor-pointer flex-col gap-4 rounded-2xl border-2 p-5 transition-colors duration-200 ${
              selected
                ? 'border-ises-green bg-ises-green/[0.08]'
                : 'border-gray-100 bg-white hover:border-ises-green/40 hover:bg-canvas-muted/50'
            } ${disabled ? 'pointer-events-none opacity-50' : ''}`}
          >
            <input
              type="radio"
              name="invoice-format"
              value={option.id}
              checked={selected}
              disabled={disabled}
              onChange={() => onChange(option.id)}
              className="sr-only"
            />
            <div className="flex items-start justify-between gap-2">
              <span
                className={`flex h-11 w-11 items-center justify-center rounded-full transition-colors ${
                  selected
                    ? 'bg-ises-green text-white'
                    : 'bg-gray-100 text-on-surface-variant'
                }`}
              >
                <MaterialIcon name="calendar_today" className="text-[24px]" />
              </span>
              {selected && (
                <MaterialIcon name="check_circle" className="text-[20px] text-ises-green" />
              )}
            </div>
            <div>
              <span className="block text-sm font-bold text-on-surface">{option.label}</span>
              <span className="mt-1 block text-xs text-on-surface-variant">
                Plantilla {option.id}
              </span>
            </div>
          </label>
        );
      })}
    </div>
  );
}
