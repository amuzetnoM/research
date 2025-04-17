// DEPRECATED: WebSocket service for environment monitoring is no longer supported.
// Use dataService (REST/SSE) from /dataService/files/dataService.ts instead.

export const createEnvironmentMonitoringSocket = () => {
  throw new Error(
    'WebSocket environment monitoring is deprecated. Use dataService (REST/SSE) for real-time metrics. See /dataService/files/dataService.ts.'
  );
};
