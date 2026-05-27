export const APP_MODULES = {
  extraction: {
    id: 'extraction',
    icon: 'receipt_long',
    label: 'Extracción de facturas',
    enabled: true,
    headerTitle: 'Extracción de facturas',
    headerSubtitle:
      'Elija Air-e o Afinia, cargue un ZIP y obtenga el consolidado Excel con detección automática de año.',
  },
  formap: {
    id: 'formap',
    icon: 'description',
    label: 'Formato Formap',
    enabled: true,
    headerTitle: 'Formato Formap',
    headerSubtitle:
      'Suba el Excel de auditoría Formap y descargue el informe unificado y ordenado.',
  },
  network: {
    id: 'network',
    icon: 'hub',
    label: 'Analizadores de red',
    enabled: false,
    headerTitle: 'Analizadores de red',
    headerSubtitle: 'Próximamente.',
  },
  dashboard: {
    id: 'dashboard',
    icon: 'dashboard',
    label: 'Dashboard',
    enabled: false,
    headerTitle: 'Dashboard',
    headerSubtitle: 'Próximamente.',
  },
};

export const MODULE_ORDER = ['extraction', 'formap', 'network', 'dashboard'];

export const DEFAULT_MODULE_ID = 'extraction';
