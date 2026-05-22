import { createContext, useContext, useEffect, useState } from 'react';
import { fetchHealth } from '../api/health.js';
import { DEFAULT_MAX_ZIP_BYTES } from '../config/api.js';

const DEFAULT_MAX_FORMAP_BYTES = 50 * 1024 * 1024;

const BackendHealthContext = createContext({
  health: null,
  maxZipBytes: DEFAULT_MAX_ZIP_BYTES,
  maxFormapExcelBytes: DEFAULT_MAX_FORMAP_BYTES,
});

export function BackendHealthProvider({ children }) {
  const [health, setHealth] = useState(null);
  const [maxZipBytes, setMaxZipBytes] = useState(DEFAULT_MAX_ZIP_BYTES);
  const [maxFormapExcelBytes, setMaxFormapExcelBytes] = useState(DEFAULT_MAX_FORMAP_BYTES);

  useEffect(() => {
    let cancelled = false;
    let retryTimer;

    const load = () => {
      fetchHealth()
        .then((data) => {
          if (cancelled) return;
          setHealth(data);
          const zipMb = data.limits?.max_zip_size_mb;
          if (zipMb) setMaxZipBytes(zipMb * 1024 * 1024);
          const formapMb = data.limits?.max_formap_excel_mb;
          if (formapMb) setMaxFormapExcelBytes(formapMb * 1024 * 1024);
        })
        .catch(() => {
          if (!cancelled) {
            setHealth({ status: 'unreachable', openai_configured: false });
            retryTimer = window.setTimeout(load, 8000);
          }
        });
    };

    load();

    return () => {
      cancelled = true;
      if (retryTimer) window.clearTimeout(retryTimer);
    };
  }, []);

  return (
    <BackendHealthContext.Provider value={{ health, maxZipBytes, maxFormapExcelBytes }}>
      {children}
    </BackendHealthContext.Provider>
  );
}

export function useBackendHealth() {
  return useContext(BackendHealthContext);
}
