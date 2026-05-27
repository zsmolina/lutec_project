/** Orden de presentación de formatos detectados en resultados de lote. */
const FORMAT_SORT_ORDER = ['2023', '2024', '2025_2026'];

const FORMAT_SHORT_LABELS = {
  '2023': '2023',
  '2024': '2024',
  '2025_2026': '2025/2026',
};

/**
 * Agrupa outcomes por format_detected y devuelve líneas «año: cantidad».
 * @param {Array<{ format_detected?: string, format_label?: string }>} outcomes
 */
export function summarizeDetectedFormats(outcomes) {
  const counts = new Map();

  for (const item of outcomes ?? []) {
    const key = item.format_detected;
    if (!key) continue;
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }

  const sortedKeys = [...counts.keys()].sort((a, b) => {
    const ia = FORMAT_SORT_ORDER.indexOf(a);
    const ib = FORMAT_SORT_ORDER.indexOf(b);
    if (ia === -1 && ib === -1) return a.localeCompare(b);
    if (ia === -1) return 1;
    if (ib === -1) return -1;
    return ia - ib;
  });

  return sortedKeys.map((key) => ({
    key,
    label: FORMAT_SHORT_LABELS[key] ?? key.replace(/_/g, '/'),
    count: counts.get(key),
  }));
}

/** Texto compacto para la tarjeta de resumen (un año o varios). */
export function formatSummaryHeadline(outcomes) {
  const rows = summarizeDetectedFormats(outcomes);
  if (rows.length === 0) return null;
  if (rows.length === 1) {
    return `${rows[0].label} (${rows[0].count})`;
  }
  return rows.map((r) => `${r.label}: ${r.count}`).join(' · ');
}
