import { create } from 'zustand';
import { persist } from 'zustand/middleware';

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

export default useAppStore;