import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { EnvironmentMonitor } from '../EnvironmentMonitor';
import { useEnvironmentMonitoring } from '../../../hooks/useEnvironmentMonitoring';

// Mock the hook
jest.mock('../../../hooks/useEnvironmentMonitoring');
const mockUseEnvironmentMonitoring = useEnvironmentMonitoring as jest.MockedFunction<typeof useEnvironmentMonitoring>;

// Mock visualizations
jest.mock('../../visualizations/LineChart', () => ({
  LineChart: () => <div data-testid="line-chart">Line Chart</div>
}));

jest.mock('../../visualizations/GaugeChart', () => ({
  GaugeChart: ({ value }: { value: number }) => (
    <div data-testid="gauge-chart">Gauge: {value}%</div>
  )
}));

// Setup wrapper with React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

// Test mock data
const mockMetrics = {
  cpu: {
    usage: 42,
    temperature: 58,
    cores: 8
  },
  memory: {
    total: 16000000000,
    used: 8000000000,
    free: 8000000000,
    usagePercentage: 50
  },
  network: {
    bytesIn: 1000000,
    bytesOut: 500000,
    packetsIn: 1000,
    packetsOut: 500
  },
  storage: {
    total: 1000000000000,
    used: 400000000000,
    free: 600000000000,
    usagePercentage: 40
  },
  processes: {
    total: 100,
    running: 80
  },
  timestamp: '2023-01-01T00:00:00Z'
};

const mockStatus = {
  status: 'healthy',
  uptime: 86400,
  alerts: []
};

describe('EnvironmentMonitor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('should show loading state', () => {
    mockUseEnvironmentMonitoring.mockReturnValue({
      metrics: null,
      status: null,
      isLoading: true,
      isError: false,
      error: null,
      lastUpdated: null,
      refresh: jest.fn()
    });
    
    render(<EnvironmentMonitor />);
    
    expect(screen.getByText(/loading environment data/i)).toBeInTheDocument();
  });
  
  test('should show error state', () => {
    mockUseEnvironmentMonitoring.mockReturnValue({
      metrics: null,
      status: null,
      isLoading: false,
      isError: true,
      error: new Error('Failed to load'),
      lastUpdated: null,
      refresh: jest.fn()
    });
    
    render(<EnvironmentMonitor />);
    
    expect(screen.getByText(/failed to load environment data/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });
  
  test('should render metrics when data is available', () => {
    const refresh = jest.fn();
    mockUseEnvironmentMonitoring.mockReturnValue({
      metrics: mockMetrics,
      status: mockStatus,
      isLoading: false,
      isError: false,
      error: null,
      lastUpdated: new Date(),
      refresh
    });
    
    render(<EnvironmentMonitor containerId="container1" />);
    
    // Check title
    expect(screen.getByText(/environment: container1/i)).toBeInTheDocument();
    
    // Check that gauge charts are rendered
    const gaugeCharts = screen.getAllByTestId('gauge-chart');
    expect(gaugeCharts.length).toBeGreaterThan(0);
    
    // Check that CPU usage is displayed
    expect(screen.getByText(/cpu usage/i)).toBeInTheDocument();
    expect(screen.getByText(/temperature: 58°c/i)).toBeInTheDocument();
    
    // Check that memory usage is displayed
    expect(screen.getByText(/memory usage/i)).toBeInTheDocument();
    
    // Check that Disk usage is displayed
    expect(screen.getByText(/disk usage/i)).toBeInTheDocument();
  });
  
  test('should pass the correct props to useEnvironmentMonitoring', () => {
    mockUseEnvironmentMonitoring.mockReturnValue({
      metrics: mockMetrics,
      status: mockStatus,
      isLoading: false,
      isError: false,
      error: null,
      lastUpdated: new Date(),
      refresh: jest.fn()
    });
    
    render(<EnvironmentMonitor containerId="container2" />);
    
    expect(mockUseEnvironmentMonitoring).toHaveBeenCalledWith({
      containerId: 'container2',
      useWebSockets: true
    });
  });
});
