import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import React, { createContext, useContext, ReactNode } from 'react';

// Define the store state interface
interface AppState {
  // Theme
  darkMode: boolean;
  toggleDarkMode: () => void;
  
  // UI State
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  
  // User Preferences
  selectedTimeRange: string;
  setSelectedTimeRange: (range: string) => void;
  
  // Dashboard Configuration
  dashboardLayout: Record<string, any>;
  updateDashboardLayout: (layout: Record<string, any>) => void;
}

// Create the store
const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial state
      darkMode: window.matchMedia('(prefers-color-scheme: dark)').matches,
      sidebarOpen: true,
      selectedTimeRange: '24h',
      dashboardLayout: {},
      
      // Actions
      toggleDarkMode: () => set((state) => {
        const newDarkMode = !state.darkMode;
        // Update document class for Tailwind dark mode
        if (newDarkMode) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
        return { darkMode: newDarkMode };
      }),
      
      toggleSidebar: () => set((state) => ({ 
        sidebarOpen: !state.sidebarOpen 
      })),
      
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      
      setSelectedTimeRange: (range) => set({ 
        selectedTimeRange: range 
      }),
      
      updateDashboardLayout: (layout) => set({ 
        dashboardLayout: layout 
      }),
    }),
    {
      name: 'research-dashboard-storage',
      partialize: (state) => ({
        darkMode: state.darkMode,
        selectedTimeRange: state.selectedTimeRange,
        dashboardLayout: state.dashboardLayout,
      }),
    }
  )
);

// Create context for AppStore
const AppStoreContext = createContext<ReturnType<typeof useAppStore> | null>(null);

// Create provider component
export const AppStoreProvider: React.FC<{children: ReactNode}> = ({ children }) => {
  // This is a workaround for using zustand with React context
  const [store] = React.useState(() => useAppStore);
  
  return (
    <AppStoreContext.Provider value={store}>
      {children}
    </AppStoreContext.Provider>
  );
};

// Hook to use app store in components
export const useAppStoreContext = () => {
  const store = useContext(AppStoreContext);
  if (!store) {
    throw new Error("useAppStoreContext must be used within AppStoreProvider");
  }
  return store;
};

export default useAppStore;