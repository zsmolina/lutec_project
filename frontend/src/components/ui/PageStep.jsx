export function PageStep({ step, title, description, children, className = '' }) {
  return (
    <section className={`soft-card ${className}`}>
      <div className="flex flex-col gap-6 p-6 lg:gap-7 lg:p-8">
        <div className="flex items-start gap-4">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-ises-green text-sm font-bold text-white">
            {step}
          </span>
          <div className="min-w-0 flex-1 pt-0.5">
            <h3 className="text-lg font-bold text-on-surface">{title}</h3>
            {description && (
              <p className="mt-1.5 max-w-2xl text-sm leading-relaxed text-on-surface-variant">
                {description}
              </p>
            )}
          </div>
        </div>
        <div className="lg:pl-14">{children}</div>
      </div>
    </section>
  );
}
