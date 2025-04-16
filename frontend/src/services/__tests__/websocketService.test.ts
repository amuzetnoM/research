import { WebSocketService, WebSocketReadyState } from '../websocketService';

// Mock WebSocket
class MockWebSocket {
  url: string;
  readyState: number = WebSocketReadyState.CONNECTING;
  onopen: ((event: any) => void) | null = null;
  onmessage: ((event: any) => void) | null = null;
  onerror: ((event: any) => void) | null = null;
  onclose: ((event: any) => void) | null = null;
  
  constructor(url: string) {
    this.url = url;
    
    // Simulate connection after a delay
    setTimeout(() => {
      this.readyState = WebSocketReadyState.OPEN;
      if (this.onopen) this.onopen({});
    }, 50);
  }
  
  send(data: string): void {
    // Mock implementation
  }
  
  close(): void {
    this.readyState = WebSocketReadyState.CLOSED;
    if (this.onclose) this.onclose({ code: 1000, reason: 'Normal closure', wasClean: true });
  }
  
  // Helper to simulate receiving a message
  simulateMessage(data: any): void {
    if (this.onmessage) {
      this.onmessage({ data: JSON.stringify(data) });
    }
  }
  
  // Helper to simulate an error
  simulateError(): void {
    if (this.onerror) {
      this.onerror(new Event('error'));
    }
  }
}

// Mock global WebSocket
global.WebSocket = MockWebSocket as any;

// Mock logger
jest.mock('@utils/logger', () => ({
  logger: {
    info: jest.fn(),
    debug: jest.fn(),
    warn: jest.fn(),
    error: jest.fn()
  }
}));

describe('WebSocketService', () => {
  let service: WebSocketService;
  
  beforeEach(() => {
    service = new WebSocketService('ws://localhost:8080');
    jest.clearAllMocks();
  });
  
  test('should connect successfully', done => {
    service.connect();
    
    // Use setTimeout to wait for the mock connection to complete
    setTimeout(() => {
      expect(service.getReadyState()).toBe(WebSocketReadyState.OPEN);
      done();
    }, 100);
  });
  
  test('should handle messages correctly', done => {
    const messageHandler = jest.fn();
    
    service.connect();
    service.onMessage('metrics', messageHandler);
    
    // Wait for connection
    setTimeout(() => {
      // Access private socket property for testing
      const mockSocket = (service as any).socket as MockWebSocket;
      
      // Simulate receiving a message
      mockSocket.simulateMessage({
        type: 'metrics',
        data: { cpu: 50, memory: 80 }
      });
      
      expect(messageHandler).toHaveBeenCalledWith({ cpu: 50, memory: 80 });
      done();
    }, 100);
  });
  
  test('should handle disconnection', done => {
    service.connect();
    
    // Wait for connection
    setTimeout(() => {
      service.disconnect();
      expect(service.getReadyState()).toBe(WebSocketReadyState.CLOSED);
      done();
    }, 100);
  });
  
  test('should throw error when sending message while disconnected', () => {
    expect(() => {
      service.send('test', { data: 'test' });
    }).toThrow();
  });
});
