// Create this file if it doesn't exist already

/**
 * Websocket service for real-time environment monitoring
 */

export const createEnvironmentMonitoringSocket = (containerId: string, onMessage: (data: any) => void) => {
  // Basic implementation for the websocket connection
  const socket = new WebSocket(`ws://localhost:8888/api/${containerId}/ws`);
  
  socket.onopen = () => {
    console.log(`WebSocket connection established for ${containerId}`);
  };
  
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing websocket message:', error);
    }
  };
  
  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  socket.onclose = () => {
    console.log(`WebSocket connection closed for ${containerId}`);
  };
  
  return {
    close: () => socket.close(),
    send: (data: any) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
      }
    }
  };
};
