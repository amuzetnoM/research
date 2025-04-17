import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { logger } from '@/utils/logger';
import { configService } from '@/utils/configService';
import { 
  getContainerMetrics, 
  getContainerHealth,
  analyzeContainerMetrics,
  generateTimeSeriesData,
  generateComparisonData
} from '@services/monitoringService';

// State types
export interface ContainerMetadata {
  id: string;
  name: string;
  status: 'running' | 'warning' | 'error' | 'stopped';
  uptime: string;
  version: string;
  lastRestart: string;
}

export interface Metrics {
  cpu: number;
  memory: number;
  network: number;
  disk: number;
  requests?: number;
  errors?: number;
}

export interface TimeSeriesPoint {
  timestamp: number;
  [key: string]: number | string;
}

export interface DashboardState {
  // Data
  container1: {
    metadata: ContainerMetadata;
    metrics: Metrics;
    timeSeriesData: TimeSeriesPoint[];
    analysis: string;
  };
  container2: {
    metadata: ContainerMetadata;
    metrics: Metrics;
    timeSeriesData: TimeSeriesPoint[];
    analysis: string;
  };
  comparisonData: any[];
  
  // UI state
  selectedTimeRange: string;
  refreshInterval: number;
  lastUpdated: string;
  isLoading: boolean;
  error: string | null;
}

// Action types
type ActionType = 
  | { type: 'SET_TIME_RANGE'; payload: string }
  | { type: 'SET_REFRESH_INTERVAL'; payload: number }
  | { type: 'START_LOADING' }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'UPDATE_CONTAINER_1'; payload: Partial<DashboardState['container1']> }
  | { type: 'UPDATE_CONTAINER_2'; payload: Partial<DashboardState['container2']> }
  | { type: 'UPDATE_COMPARISON_DATA'; payload: any[] }
  | { type: 'REFRESH_DATA_SUCCESS' }
  | { type: 'RESET_DASHBOARD' };

// Initial state
const initialState: DashboardState = {
  container1: {
    metadata: {
      id: 'container1',
      name: 'Research Container 1',
      status: 'running',
      uptime: '0d 0h 0m',
      version: '0.0.0',
      lastRestart: new Date().toISOString(),
    },
    metrics: {
      cpu: 0,
      memory: 0,
      network: 0,
      disk: 0,
      requests: 0,
      errors: 0,
    },
    timeSeriesData: [],
    analysis: '',
  },
  container2: {
    metadata: {
      id: 'container2',
      name: 'Research Container 2',
      status: 'running',
      uptime: '0d 0h 0m',
      version: '0.0.0',
      lastRestart: new Date().toISOString(),
    },
    metrics: {
      cpu: 0,
      memory: 0,
      network: 0,
      disk: 0,
      requests: 0,
      errors: 0,
    },
    timeSeriesData: [],
    analysis: '',
  },
  comparisonData: [],
  selectedTimeRange: configService.getSetting('defaultTimeRange'),
  refreshInterval: configService.getSetting('refreshInterval'),
  lastUpdated: new Date().toISOString(),
  isLoading: true,
  error: null,
};

// Create context
const DashboardContext = createContext<{
  state: DashboardState;
  dispatch: React.Dispatch<ActionType>;
  refreshData: () => Promise<void>;
  getPointsForTimeRange: (range: string) => number;
  getIntervalForTimeRange: (range: string) => number;
}>({
  state: initialState,
  dispatch: () => null,
  refreshData: async () => {},
  getPointsForTimeRange: () => 24,
  getIntervalForTimeRange: () => 3600000,
});

// Reducer function
const dashboardReducer = (state: DashboardState, action: ActionType): DashboardState => {
  switch (action.type) {
    case 'SET_TIME_RANGE':
      return {
        ...state,
        selectedTimeRange: action.payload,
      };
    case 'SET_REFRESH_INTERVAL':
      return {
        ...state,
        refreshInterval: action.payload,
      };
    case 'START_LOADING':
      return {
        ...state,
        isLoading: true,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };
    case 'UPDATE_CONTAINER_1':
      return {
        ...state,
        container1: {
          ...state.container1,
          ...action.payload,
        },
      };
    case 'UPDATE_CONTAINER_2':
      return {
        ...state,
        container2: {
          ...state.container2,
          ...action.payload,
        },
      };
    case 'UPDATE_COMPARISON_DATA':
      return {
        ...state,
        comparisonData: action.payload,
      };
    case 'REFRESH_DATA_SUCCESS':
      return {
        ...state,
        lastUpdated: new Date().toISOString(),
        isLoading: false,
        error: null,
      };
    case 'RESET_DASHBOARD':
      return {
        ...initialState,
        selectedTimeRange: state.selectedTimeRange,
        refreshInterval: state.refreshInterval,
      };
    default:
      return state;
  }
};

// Provider component
export const DashboardProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(dashboardReducer, initialState);
  
  // Helper functions
  const getPointsForTimeRange = (range: string): number => {
    switch (range) {
      case '1h': return 60; // 1 point per minute
      case '6h': return 72; // 1 point per 5 minutes
      case '12h': return 72; // 1 point per 10 minutes
      case '24h': return 96; // 1 point per 15 minutes
      case '7d': return 84; // 1 point per 2 hours
      case '30d': return 90; // 1 point per 8 hours
      default: return 24;
    }
  };

  const getIntervalForTimeRange = (range: string): number => {
    switch (range) {
      case '1h': return 60 * 1000; // 1 minute
      case '6h': return 5 * 60 * 1000; // 5 minutes
      case '12h': return 10 * 60 * 1000; // 10 minutes
      case '24h': return 15 * 60 * 1000; // 15 minutes
      case '7d': return 2 * 60 * 60 * 1000; // 2 hours
      case '30d': return 8 * 60 * 60 * 1000; // 8 hours
      default: return 60 * 60 * 1000; // 1 hour
    }
  };
  
  // Refresh data function
  const refreshData = async () => {
    dispatch({ type: 'START_LOADING' });
    
    try {
      // Get points and interval based on selected time range
      const points = getPointsForTimeRange(state.selectedTimeRange);
      const interval = getIntervalForTimeRange(state.selectedTimeRange);
      
      // Fetch container 1 data
      const container1Data = await getContainerMetrics('container1');
      const container1Health = await getContainerHealth('container1').catch(() => ({ status: 'warning' }));
      const container1Analysis = await analyzeContainerMetrics('container1', state.selectedTimeRange);
      
      // Update container 1 in state
      dispatch({
        type: 'UPDATE_CONTAINER_1',
        payload: {
          metadata: {
            id: 'container1',
            name: 'Research Container 1',
            status: container1Health.status as any,
            uptime: container1Data.uptime,
            version: container1Data.version || '1.0.0',
            lastRestart: container1Data.lastRestart || new Date().toISOString(),
          },
          metrics: {
            cpu: container1Data.cpu.usage,
            memory: container1Data.memory.percentage,
            network: container1Data.network.rx + container1Data.network.tx,
            disk: container1Data.disk?.percentage || 0,
            requests: Math.round(Math.random() * 150 + 150), // Mock data
            errors: container1Data.errorRate || 0,
          },
          timeSeriesData: generateTimeSeriesData(points, interval),
          analysis: container1Analysis,
        },
      });
      
      // Fetch container 2 data
      const container2Data = await getContainerMetrics('container2');
      const container2Health = await getContainerHealth('container2').catch(() => ({ status: 'warning' }));
      const container2Analysis = await analyzeContainerMetrics('container2', state.selectedTimeRange);
      
      // Update container 2 in state
      dispatch({
        type: 'UPDATE_CONTAINER_2',
        payload: {
          metadata: {
            id: 'container2',
            name: 'Research Container 2',
            status: container2Health.status as any,
            uptime: container2Data.uptime,
            version: container2Data.version || '1.0.0',
            lastRestart: container2Data.lastRestart || new Date().toISOString(),
          },
          metrics: {
            cpu: container2Data.cpu.usage,
            memory: container2Data.memory.percentage,
            network: container2Data.network.rx + container2Data.network.tx,
            disk: container2Data.disk?.percentage || 0,
            requests: Math.round(Math.random() * 150 + 150), // Mock data
            errors: container2Data.errorRate || 0,
          },
          timeSeriesData: generateTimeSeriesData(points, interval),
          analysis: container2Analysis,
        },
      });
      
      // Update comparison data
      dispatch({
        type: 'UPDATE_COMPARISON_DATA',
        payload: generateComparisonData(),
      });
      
      // Update success
      dispatch({ type: 'REFRESH_DATA_SUCCESS' });
      logger.info('Dashboard data refreshed', { timeRange: state.selectedTimeRange });
      
    } catch (error) {
      logger.error('Failed to refresh dashboard data', { error });
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to load dashboard data' 
      });
    }
  };
  
  // Initial data load
  useEffect(() => {
    refreshData();
  }, []);
  
  // Auto-refresh based on interval
  useEffect(() => {
    if (state.refreshInterval > 0) {
      const timerId = setInterval(refreshData, state.refreshInterval);
      return () => clearInterval(timerId);
    }
  }, [state.refreshInterval, state.selectedTimeRange]);
  
  // Update when time range changes
  useEffect(() => {
    refreshData();
  }, [state.selectedTimeRange]);
  
  // Context value
  const contextValue = {
    state,
    dispatch,
    refreshData,
    getPointsForTimeRange,
    getIntervalForTimeRange,
  };

  return (
    <DashboardContext.Provider value={contextValue}>
      {children}
    </DashboardContext.Provider>
  );
};

// Custom hook to use the dashboard context
export const useDashboard = () => {
  const context = useContext(DashboardContext);
  if (context === undefined) {
    throw new Error('useDashboard must be used within a DashboardProvider');
  }
  return context;
};

// Add this named export for the hook
export const useDashboardContext = () => {
  const context = useContext(DashboardContext);
  if (context === undefined) {
    throw new Error('useDashboardContext must be used within a DashboardProvider');
  }
  return context;
};
