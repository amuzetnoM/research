import React, { ReactNode } from 'react';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import useAppStore from '../../store/appStore';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { sidebarOpen } = useAppStore();

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Subtle Gradient Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-primary-50 to-background -z-10"></div>
      
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
        {/* Top Navbar */}
        <Navbar />
        
        {/* Main Content Area */}
        <main className="flex-1 overflow-auto p-5 pb-10 space-y-6 animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
