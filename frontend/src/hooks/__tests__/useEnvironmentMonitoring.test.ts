import { renderHook, act } from '@testing-library/react-hooks';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEnvironmentMonitoring } from '../useEnvironmentMonitoring';
import apiClient from '../../services/api';
import { createEnvironmentMonitoringSocket } from '../../services/websocketService';

// Mock dependencies
jest.mock('../../services/api');
jest.mock('../../services/websocketService');

const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;
const mockCreateSocket = createEnvironmentMonitoringSocket as jest.MockedFunction<typeof createEnvironmentMonitoringSocket>;

// Mock socket implementation
const mockSocket = {
  connect: jest.fn(),
  disconnect: jest.fn(),
  onMessage: jest.fn().mockImplementation((type, handler) => {
    // Store the handler for later use in tests
    mockSocket.handlers[type] = handler;
    return jest.fn(); // Return unsubscribe function
  }),
  handlers: {} as Record<string, (data: any) => void>,
  // Helper to simulate receiving a message
  simulateMessage: function(type: string, data: any) {
    if (this.handlers[type]) {
      this.handlers[type](data);
    }
  }
};

mockCreateSocket.mockReturnValue(mockSocket as any);

// Mock API responses
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

mockApiClient.get.mockImplementation((url) => {
  if (url.includes('metrics')) {
    return Promise.resolve({ data: mockMetrics });
  }
  if (url.includes('status')) {
    return Promise.resolve({ data: mockStatus });
  }
  return Promise.reject(new Error('Not found'));
});

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

describe('useEnvironmentMonitoring', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('should fetch initial data via REST API', async () => {
    const { result, waitFor } = renderHook(() => 
      useEnvironmentMonitoring({ useWebSockets: false }), 
      { wrapper }
    );
    
    // Initially loading
    expect(result.current.isLoading).toBe(true);
    
    // Wait for data to load
    await waitFor(() => !result.current.isLoading);
    
    // Verify API was called
    expect(mockApiClient.get).toHaveBeenCalledWith('/monitoring/metrics');
    expect(mockApiClient.get).toHaveBeenCalledWith('/monitoring/status');
    
    // Verify data was loaded
    expect(result.current.metrics).toEqual(mockMetrics);
    expect(result.current.status).toEqual(mockStatus);
    expect(result.current.isError).toBe(false);
  });
  
  test('should use WebSockets when enabled', async () => {
    const { result, waitFor } = renderHook(() => 
      useEnvironmentMonitoring({ useWebSockets: true }), 
      { wrapper }
    );
    
    // Wait for initial data load
    await waitFor(() => !result.current.isLoading);
    
    // Verify WebSocket connection was made
    expect(mockCreateSocket).toHaveBeenCalled();
    expect(mockSocket.connect).toHaveBeenCalled();
    expect(mockSocket.onMessage).toHaveBeenCalledWith('metrics', expect.any(Function));
    expect(mockSocket.onMessage).toHaveBeenCalledWith('status', expect.any(Function));
    
    // Simulate receiving WebSocket updates
    const updatedMetrics = { ...mockMetrics, cpu: { ...mockMetrics.cpu, usage: 60 } };
    
    act(() => {
      mockSocket.simulateMessage('metrics', updatedMetrics);
    });
    
    // Verify data was updated
    expect(result.current.metrics).toEqual(updatedMetrics);
  });
  
  test('should use container-specific endpoints when containerId is provided', async () => {
    renderHook(() => 
      useEnvironmentMonitoring({ containerId: 'container1', useWebSockets: false }), 
      { wrapper }
    );
    
    // Wait for API calls to complete
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Verify container-specific API endpoints were used
    expect(mockApiClient.get).toHaveBeenCalledWith('/monitoring/container1/metrics');
    expect(mockApiClient.get).toHaveBeenCalledWith('/monitoring/container1/status');
  });
  
  test('should properly clean up WebSocket connection on unmount', async () => {
    const { unmount, waitFor } = renderHook(() => 
      useEnvironmentMonitoring({ useWebSockets: true }), 
      { wrapper }
    );
    
    // Wait for initial setup
    await waitFor(() => expect(mockSocket.connect).toHaveBeenCalled());
    
    // Unmount the component
    unmount();
    
    // Verify WebSocket was disconnected
    expect(mockSocket.disconnect).toHaveBeenCalled();
  });
  
  test('should refresh data when refresh method is called', async () => {
    const { result, waitFor } = renderHook(() => 
      useEnvironmentMonitoring({ useWebSockets: false }), 
      { wrapper }
    );
    
    // Wait for initial data load
    await waitFor(() => !result.current.isLoading);
    
    // Clear mock to check for new calls
    mockApiClient.get.mockClear();
    
    // Call refresh
    act(() => {
      result.current.refresh();
    });
    
    // Verify API was called again
    expect(mockApiClient.get).toHaveBeenCalledWith('/monitoring/metrics');
    expect(mockApiClient.get).toHaveBeenCalledWith('/monitoring/status');
  });
});
