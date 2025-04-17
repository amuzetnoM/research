import React from 'react';
import useAppStore from '../../store/appStore';

const Navbar: React.FC = () => {
  const { toggleDarkMode, darkMode } = useAppStore();

  return (
    <nav className="glass border-thin border-white/20 backdrop-blur-md sticky top-0 z-10 px-5 py-3 mx-4 mt-3 rounded-xl shadow-glass-sm">
      <div className="flex justify-between items-center">
        <div className="flex items-center">
          <span className="text-lg font-medium accent">Research Dashboard</span>
        </div>
        <div className="flex items-center gap-3">
          {/* Theme Toggle */}
          <button 
            onClick={toggleDarkMode}
            className="neumorph-sm border-thin border-white/20 p-2 rounded-lg text-foreground/80 hover:text-primary-500 transition-all duration-200"
            aria-label="Toggle theme"
          >
            {darkMode ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
            )}
          </button>
          {/* User/Profile Button */}
          <button className="glass-sm border-thin border-white/20 flex items-center py-1.5 pl-2 pr-3 rounded-lg hover:shadow-glass-sm transition-all duration-200">
            <div className="w-7 h-7 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs font-medium mr-2">
              RD
            </div>
            <span className="text-sm font-medium text-foreground/80 hidden sm:inline">User</span>
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
