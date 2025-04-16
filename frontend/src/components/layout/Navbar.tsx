import React from 'react';
import useAppStore from '../../store/appStore';

const Navbar: React.FC = () => {
  const { toggleDarkMode, darkMode } = useAppStore();

  return (
    <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-2.5 shadow-sm">
      <div className="flex justify-between items-center">
        <div className="flex items-center">
          <span className="text-lg font-semibold text-gray-800 dark:text-white">Research Dashboard</span>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Theme Toggle */}
          <button 
            onClick={toggleDarkMode}
            className="p-2 rounded-full text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            {darkMode ? (
              <span className="material-icons-outlined">light_mode</span>
            ) : (
              <span className="material-icons-outlined">dark_mode</span>
            )}
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
