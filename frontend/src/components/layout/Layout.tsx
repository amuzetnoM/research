import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { useTheme } from '@/contexts/ThemeContext';
import { cn } from '@/lib/utils';

const Layout: React.FC = () => {
  const { isDarkMode, getBackgroundStyle } = useTheme();
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  return (
    <div 
      className={cn(
        "min-h-screen transition-colors duration-500",
        isDarkMode ? "dark" : ""
      )}
      style={getBackgroundStyle()}
    >
      <Navbar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
      <div className="flex">
        <Sidebar open={sidebarOpen} />
        <main className={cn(
          "flex-1 p-4 sm:p-8 transition-all duration-300",
          sidebarOpen ? "ml-0 sm:ml-64" : "ml-0"
        )}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
