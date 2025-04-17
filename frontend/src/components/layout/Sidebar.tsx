import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import useAppStore from '../../store/appStore';

const Sidebar: React.FC = () => {
  const { sidebarOpen, toggleSidebar } = useAppStore();
  const location = useLocation();

  const menuItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/research', label: 'Research' },
    { path: '/models', label: 'Models' },
    { path: '/analytics', label: 'Analytics' },
    { path: '/publications', label: 'Publications' },
    { path: '/settings', label: 'Settings' },
  ];

  return (
    <aside
      className={`fixed inset-y-0 left-0 bg-surface border-r border-base transition-all duration-300 z-30 flex flex-col ${sidebarOpen ? 'w-56' : 'w-16'}`}
      aria-label="Main navigation"
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-base">
        {sidebarOpen && (
          <span className="text-lg font-bold tracking-tight text-foreground">Research Platform</span>
        )}
        <button
          onClick={toggleSidebar}
          className="p-2 rounded transition-base hover:bg-background-alt focus:outline-none"
          aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {/* Simple SVG hamburger/close icon */}
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
                  className={`block px-4 py-2 rounded text-base font-medium transition-base
                    ${isActive ? 'bg-primary/10 text-primary font-semibold' : 'text-foreground/80 hover:bg-background-alt'}
                    text-left w-full`}
                  tabIndex={0}
                >
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      {/* Version or footer (optional, minimal) */}
      <div className="px-4 py-3 border-t border-base text-xs text-muted text-center">
        v0.1.0
      </div>
    </aside>
  );
};

export default Sidebar;
