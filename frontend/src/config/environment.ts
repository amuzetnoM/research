interface EnvironmentConfig {
  apiBaseUrl: string;
  websocketUrl: string;
  refetchInterval: number;
  grafana: {
    container1Url: string;
    container2Url: string;
    defaultDashboard: string;
  };
  prometheus: {
    container1Url: string;
    container2Url: string;
    queryEndpoint: string;
  };
}

const config: EnvironmentConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '',
  websocketUrl: import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8888/ws',
  refetchInterval: parseInt(import.meta.env.VITE_REFETCH_INTERVAL || '5000'),
  grafana: {
    container1Url: 'http://localhost:3000',
    container2Url: 'http://localhost:3001',
    defaultDashboard: 'research-overview'
  },
  prometheus: {
    container1Url: 'http://localhost:9090',
    container2Url: 'http://localhost:9091',
    queryEndpoint: '/api/v1/query'
  }
};

export default config;
