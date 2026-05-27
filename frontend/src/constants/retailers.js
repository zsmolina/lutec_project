/** Comercializadores soportados (debe coincidir con backend EnergyRetailer). */
export const RETAILERS = [
  {
    id: 'aire',
    label: 'Air-e',
    description: 'Facturas 2023, 2024 y 2025/2026. Detección automática por año.',
    icon: 'bolt',
  },
  {
    id: 'afinia',
    label: 'Afinia',
    description: '2024: hoja única. 2025/2026: dos hojas PDF. Detección automática por año.',
    icon: 'electric_bolt',
  },
];

export const DEFAULT_RETAILER_ID = 'aire';
