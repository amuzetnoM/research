import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { EnvironmentComparison } from '../EnvironmentComparison';
import { useEnvironmentMonitoring } from '../../../hooks/useEnvironmentMonitoring';

// Mock the hook
jest.mock('../../../hooks/useEnvironmentMonitoring');
const mockUseEnvironmentMonitoring = useEnvironmentMonitoring as jest.MockedFunction<typeof useEnvironmentMonitoring>;

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
const mockMetrics1 = {
  cpu: {
    usage: 40,
    temperature: 55,
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

const mockMetrics2 = {
  cpu: {
    usage: 60,
    temperature: 65,
    cores: 8
  },
  memory: {
    total: 16000000000,
    used: 12000000000,
    free: 4000000000,
    usagePercentage: 75
  },
  network: {
    bytesIn: 2000000,
    bytesOut: 1000000,
    packetsIn: 2000,
    packetsOut: 1000
  },
  storage: {
    total: 1000000000000,
    used: 600000000000,
    free: 400000000000,
    usagePercentage: 60
  },
  processes: {
    total: 100,
    running: 90
  },
  timestamp: '2023-01-01T00:00:00Z'
};

const mockStatus = {
  status: 'healthy',
  uptime: 86400,
  alerts: []
};

describe('EnvironmentComparison', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup default mock implementation
    mockUseEnvironmentMonitoring.mockImplementation(({ containerId }) => {
      if (containerId === 'container1') {
        return {
          metrics: mockMetrics1,
          status: mockStatus,
          isLoading: false,
          isError: false,
          error: null,
          lastUpdated: new Date(),
          refresh: jest.fn()
        };
      } else {
        return {
          metrics: mockMetrics2,
          status: mockStatus,
          isLoading: false,
          isError: false,
          error: null,
          lastUpdated: new Date(),
          refresh: jest.fn()
        };
      }
    });
  });
  
  test('should render comparison table with correct metrics', () => {
    render(<EnvironmentComparison />);
    
    // Check title
    expect(screen.getByText('Environment Comparison')).toBeInTheDocument();
    
    // Check table headers
    expect(screen.getByText('Container 1')).toBeInTheDocument();
    expect(screen.getByText('Container 2')).toBeInTheDocument();
    expect(screen.getByText('Difference')).toBeInTheDocument();
    
    // Check CPU metrics
    expect(screen.getByText('40.0%')).toBeInTheDocument();
    expect(screen.getByText('60.0%')).toBeInTheDocument();
    expect(screen.getByText('55°C')).toBeInTheDocument();
    expect(screen.getByText('65°C')).toBeInTheDocument();
    
    // Check Memory metrics
    expect(screen.getByText('50.0%')).toBeInTheDocument();
    expect(screen.getByText('75.0%')).toBeInTheDocument();
    
    // Verify difference indicators are present
    const differenceIndicators = screen.getAllByText(/↑|↓/);
    expect(differenceIndicators.length).toBeGreaterThan(0);
  });
  
  test('should show loading state when data is loading', () => {
    mockUseEnvironmentMonitoring.mockImplementation(() => ({
      metrics: null,
      status: null,
      isLoading: true,
      isError: false,
      error: null,
      lastUpdated: null,
      refresh: jest.fn()
    }));
    
    render(<EnvironmentComparison />);
    
    expect(screen.getByText(/loading comparison data/i)).toBeInTheDocument();
  });
  
  test('should show error state when there is an error', () => {
    mockUseEnvironmentMonitoring.mockImplementation(() => ({
      metrics: null,
      status: null,
      isLoading: false,
      isError: true,
      error: new Error('Failed to load'),
      lastUpdated: null,
      refresh: jest.fn()
    }));
    
    render(<EnvironmentComparison />);
    
    expect(screen.getByText(/failed to load comparison data/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });
  
  test('should show warning when data is incomplete', () => {
    mockUseEnvironmentMonitoring.mockImplementation(({ containerId }) => {
      if (containerId === 'container1') {
        return {
          metrics: null, // Missing metrics
          status: mockStatus,
          isLoading: false,
          isError: false,
          error: null,
          lastUpdated: new Date(),
          refresh: jest.fn()
        };
      } else {
        return {
          metrics: mockMetrics2,
          status: mockStatus,
          isLoading: false,
          isError: false,
          error: null,
          lastUpdated: new Date(),
          refresh: jest.fn()
        };
      }
    });
    
    render(<EnvironmentComparison />);
    
    expect(screen.getByText(/incomplete data/i)).toBeInTheDocument();
    expect(screen.getByText(/some environment metrics are missing/i)).toBeInTheDocument();
  });
  
  test('should call refresh for both containers when refresh button is clicked', () => {
    const refreshContainer1 = jest.fn();
    const refreshContainer2 = jest.fn();
    
    mockUseEnvironmentMonitoring.mockImplementation(({ containerId }) => {
      if (containerId === 'container1') {
        return {
          metrics: mockMetrics1,
          status: mockStatus,
          isLoading: false,
          isError: false,
          error: null,
          lastUpdated: new Date(),
          refresh: refreshContainer1
        };
      } else {
        return {
          metrics: mockMetrics2,
          status: mockStatus,
          isLoading: false,
          isError: false,
          error: null,
          lastUpdated: new Date(),
          refresh: refreshContainer2
        };
      }
    });
    
    render(<EnvironmentComparison />);
    
    // Click the refresh button
    screen.getByTitle('Refresh data').click();
    
    // Verify both refresh functions were called
    expect(refreshContainer1).toHaveBeenCalled();
    expect(refreshContainer2).toHaveBeenCalled();
  });
});
