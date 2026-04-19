import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export function Layout(): JSX.Element {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarExpanded, setSidebarExpanded] = useState(false);

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-bg-base)' }}>
      <Header onToggleSidebar={() => setSidebarOpen((v) => !v)} />
      <Sidebar
        isOpen={sidebarOpen}
        isExpanded={sidebarExpanded}
        onClose={() => setSidebarOpen(false)}
        onExpandChange={setSidebarExpanded}
      />
      <main className="transition-all duration-200 pt-14 lg:pt-0">
        <div
          className={`transition-all duration-200 ${sidebarExpanded ? 'lg:ml-[220px]' : 'lg:ml-14'}`}
        >
          <div className="p-4 lg:p-8 max-w-7xl mx-auto">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
}
