export function MaterialIcon({ name, className = 'text-[20px]' }) {
  return (
    <span className={`material-symbols-outlined ${className}`} aria-hidden>
      {name}
    </span>
  );
}
