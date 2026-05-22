import { MaterialIcon } from './MaterialIcon.jsx';

const VARIANTS = {
  primary:
    'bg-ises-green text-white hover:bg-[#94c41f] active:bg-[#86b31c] disabled:cursor-not-allowed disabled:opacity-50',
  secondary:
    'border border-outline bg-white text-on-surface hover:bg-canvas-muted active:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50',
  outline:
    'border border-ises-green/50 bg-white text-forest-green hover:bg-ises-green/8 disabled:cursor-not-allowed disabled:opacity-50',
  dark:
    'bg-forest-green text-white hover:bg-[#1e4234] active:bg-[#173528] disabled:cursor-not-allowed disabled:opacity-50',
};

const SIZES = {
  sm: 'px-4 py-2 text-xs',
  md: 'px-5 py-2.5 text-sm',
  lg: 'px-7 py-3 text-sm',
};

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  icon,
  iconSpin = false,
  ...props
}) {
  return (
    <button
      type="button"
      className={`inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-colors duration-200 ${VARIANTS[variant]} ${SIZES[size]} ${className}`}
      {...props}
    >
      {icon && (
        <MaterialIcon
          name={icon}
          className={`text-[20px] ${iconSpin ? 'animate-spin' : ''}`}
        />
      )}
      {children}
    </button>
  );
}
