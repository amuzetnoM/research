import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import useAppStore from '../../store/appStore';

const Sidebar: React.FC = () => {
  const { sidebarOpen, toggleSidebar } = useAppStore();
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { path: '/containers', label: 'Containers', icon: 'dns' },
    { path: '/frameworks', label: 'Frameworks', icon: 'extension' },
    { path: '/results', label: 'Results', icon: 'analytics' },
    { path: '/experiments', label: 'Experiments', icon: 'bubble_chart' },
    { path: '/research', label: 'Research & Publications', icon: 'menu_book' },
    { path: '/settings', label: 'Settings', icon: 'settings' },
  ];

  return (
    <aside
      className={`fixed inset-y-0 left-0 glass neumorph shadow-glass border-r border-white/20 transition-all duration-300 z-30 flex flex-col ${sidebarOpen ? 'w-56' : 'w-20'}`}
      aria-label="Main navigation"
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-white/10">
        {sidebarOpen && (
          <span className="text-lg font-bold tracking-tight accent">Research Platform</span>
        )}
        <button
          onClick={toggleSidebar}
          className="p-2 rounded transition-base hover:bg-background-alt focus:outline-none"
          aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {sidebarOpen ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
          )}
        </button>
      </div>
      {/* Navigation Items */}
      <nav className="flex-1 overflow-y-auto py-4 px-2">
        <ul className="space-y-1">
          {menuItems.map(item => {
            const isActive = location.pathname === item.path ||
              (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-2 rounded-2xl font-medium transition-base text-base ${
                    isActive ? 'bg-primary-100/40 text-primary-600' : 'text-foreground/80 hover:bg-white/10'
                  }`}
                  tabIndex={0}
                >
                  <span className="material-icons-round text-xl">{item.icon}</span>
                  {sidebarOpen && <span>{item.label}</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="px-4 py-3 border-t border-white/10 text-xs text-muted text-center">
        v0.1.0
      </div>
    </aside>
  );
};

export default Sidebar;
