import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import useAppStore from '../../store/appStore';

const Sidebar: React.FC = () => {
  const { sidebarOpen, toggleSidebar } = useAppStore();
  const location = useLocation();

  const menuItems = [
    { path: '/', label: 'Dashboard', icon: 'dashboard' },
    { path: '/containers/container1', label: 'Container 1', icon: 'view_in_ar' },
    { path: '/containers/container2', label: 'Container 2', icon: 'view_in_ar' },
  ];

  return (
    <aside 
      className={`fixed inset-y-0 left-0 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 z-30 ${
        sidebarOpen ? 'w-64' : 'w-20'
      }`}
    >
      <div className="flex flex-col h-full">
        {/* Sidebar Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700">
          {sidebarOpen && (
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white">AI Research</h2>
          )}
          <button 
            onClick={toggleSidebar}
            className="p-2 rounded-md text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <span className="material-icons-outlined">
              {sidebarOpen ? 'menu_open' : 'menu'}
            </span>
          </button>
        </div>
        
        {/* Navigation Items */}
        <nav className="flex-1 overflow-y-auto py-4">
          <ul>
            {menuItems.map(item => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center py-3 px-4 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 ${
                    location.pathname === item.path ? 'bg-gray-100 dark:bg-gray-700 text-primary-600 dark:text-primary-400' : ''
                  }`}
                >
                  <span className="material-icons-outlined">{item.icon}</span>
                  {sidebarOpen && <span className="ml-3">{item.label}</span>}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;
