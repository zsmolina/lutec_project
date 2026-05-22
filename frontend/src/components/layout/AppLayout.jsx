import { Sidebar } from './Sidebar.jsx';
import { AppHeader } from './AppHeader.jsx';

export function AppLayout({ children, headerTitle, headerSubtitle, activeModuleId, onModuleChange }) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-canvas">
      <Sidebar activeModuleId={activeModuleId} onModuleChange={onModuleChange} />
      <div className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
        <AppHeader title={headerTitle} subtitle={headerSubtitle} />
        {children}
      </div>
    </div>
  );
}
