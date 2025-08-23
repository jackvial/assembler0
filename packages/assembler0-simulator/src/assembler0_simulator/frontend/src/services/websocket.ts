import { WebSocketMessage, CameraParams } from '../types';

let globalWebSocketInstance: SimulatorWebSocket | null = null;

export class SimulatorWebSocket {
  private ws: WebSocket | null = null;
  private reconnectTimeout: number | null = null;
  private messageHandlers: ((message: WebSocketMessage) => void)[] = [];

  constructor(private url: string) {
    globalWebSocketInstance = this;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data) as WebSocketMessage;
            this.messageHandlers.forEach((handler) => handler(message));
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.scheduleReconnect();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private scheduleReconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    this.reconnectTimeout = window.setTimeout(() => {
      console.log('Attempting to reconnect...');
      this.connect();
    }, 1000);
  }

  sendControl(controls: Record<string, number>) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'control',
          data: controls,
        })
      );
    }
  }

  sendCamera(params: CameraParams) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'camera',
          data: params,
        })
      );
    }
  }

  onMessage(handler: (message: WebSocketMessage) => void) {
    this.messageHandlers.push(handler);
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    if (this.ws) {
      this.ws.close();
    }
  }

  getConnection(): WebSocket | null {
    return this.ws;
  }
}

export const getWebSocketConnection = (): WebSocket | null => {
  return globalWebSocketInstance?.getConnection() || null;
};
