import { useState } from 'react';
import { AppLayout } from './components/layout/AppLayout.jsx';
import { InvoiceExtractionPage } from './components/pages/InvoiceExtractionPage.jsx';
import { FormapFormatPage } from './components/pages/FormapFormatPage.jsx';
import { BackendHealthProvider } from './context/BackendHealthContext.jsx';
import { APP_MODULES, DEFAULT_MODULE_ID } from './constants/modules.js';

function ModuleContent({ moduleId }) {
  switch (moduleId) {
    case 'formap':
      return <FormapFormatPage />;
    case 'extraction':
    default:
      return <InvoiceExtractionPage />;
  }
}

export default function App() {
  const [activeModuleId, setActiveModuleId] = useState(DEFAULT_MODULE_ID);
  const module = APP_MODULES[activeModuleId] ?? APP_MODULES[DEFAULT_MODULE_ID];

  return (
    <BackendHealthProvider>
      <AppLayout
        activeModuleId={activeModuleId}
        onModuleChange={setActiveModuleId}
        headerTitle={module.headerTitle}
        headerSubtitle={module.headerSubtitle}
      >
        <ModuleContent moduleId={activeModuleId} />
      </AppLayout>
    </BackendHealthProvider>
  );
}
