/**
 * Watcher Service - Connects to SSE endpoint for real-time watcher activity
 */

import { API_BASE_URL } from '../config';

export interface WatcherEvent {
  timestamp: string;
  event_type: string;
  filename: string;
  file_size?: number;
  duration?: number;
  stage?: string;
  platform?: string;
  status: 'processing' | 'success' | 'error';
  message: string;
  metadata?: Record<string, any>;
}

export interface WatcherStatus {
  status: 'idle' | 'watching' | 'processing';
  timestamp: string;
}

export interface OBSStatus {
  obs_running: boolean;
  obs_installed: boolean;
  config_dir: string | null;
  active_profile: string | null;
  replay_buffer_path: string | null;
  timestamp: string;
}

type EventCallback = (event: WatcherEvent) => void;
type ErrorCallback = (error: Error) => void;
type StatusCallback = (connected: boolean) => void;

class WatcherService {
  private eventSource: EventSource | null = null;
  private baseUrl: string;
  private reconnectTimeout: number = 3000;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;
  private eventCallbacks: Set<EventCallback> = new Set();
  private errorCallbacks: Set<ErrorCallback> = new Set();
  private statusCallbacks: Set<StatusCallback> = new Set();
  private reconnectTimer: NodeJS.Timeout | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Connect to the SSE stream
   */
  connect(): void {
    if (this.eventSource) {
      console.warn('Already connected to watcher stream');
      return;
    }

    try {
      this.eventSource = new EventSource(`${this.baseUrl}/api/watcher/stream`);

      this.eventSource.onopen = () => {
        console.log('Connected to watcher stream');
        this.reconnectAttempts = 0;
        this.notifyStatus(true);
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data: WatcherEvent = JSON.parse(event.data);
          this.notifyEvent(data);
        } catch (error) {
          console.error('Error parsing event data:', error);
        }
      };

      this.eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        this.notifyStatus(false);
        this.handleReconnect();
      };
    } catch (error) {
      console.error('Error connecting to watcher stream:', error);
      this.notifyError(error as Error);
    }
  }

  /**
   * Disconnect from the SSE stream
   */
  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.notifyStatus(false);
      console.log('Disconnected from watcher stream');
    }
  }

  /**
   * Handle reconnection logic
   */
  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.disconnect();
      return;
    }

    this.disconnect();
    this.reconnectAttempts++;

    const delay = Math.min(this.reconnectTimeout * this.reconnectAttempts, 30000);
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Fetch historical events
   */
  async getHistory(): Promise<WatcherEvent[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/watcher/history`);
      if (!response.ok) {
        throw new Error('Failed to fetch history');
      }
      const data = await response.json();
      return data.events || [];
    } catch (error) {
      console.error('Error fetching history:', error);
      throw error;
    }
  }

  /**
   * Fetch current watcher status
   */
  async getStatus(): Promise<WatcherStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/api/watcher/status`);
      if (!response.ok) {
        throw new Error('Failed to fetch status');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching status:', error);
      throw error;
    }
  }

  /**
   * Clear event history
   */
  async clearHistory(): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/watcher/clear-history`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to clear history');
      }
    } catch (error) {
      console.error('Error clearing history:', error);
      throw error;
    }
  }

  /**
   * Fetch OBS status
   */
  async getOBSStatus(): Promise<OBSStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/api/obs/status`);
      if (!response.ok) {
        throw new Error('Failed to fetch OBS status');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching OBS status:', error);
      throw error;
    }
  }

  /**
   * Subscribe to watcher events
   */
  onEvent(callback: EventCallback): () => void {
    this.eventCallbacks.add(callback);
    return () => this.eventCallbacks.delete(callback);
  }

  /**
   * Subscribe to errors
   */
  onError(callback: ErrorCallback): () => void {
    this.errorCallbacks.add(callback);
    return () => this.errorCallbacks.delete(callback);
  }

  /**
   * Subscribe to connection status changes
   */
  onStatusChange(callback: StatusCallback): () => void {
    this.statusCallbacks.add(callback);
    return () => this.statusCallbacks.delete(callback);
  }

  /**
   * Notify all event callbacks
   */
  private notifyEvent(event: WatcherEvent): void {
    this.eventCallbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error('Error in event callback:', error);
      }
    });
  }

  /**
   * Notify all error callbacks
   */
  private notifyError(error: Error): void {
    this.errorCallbacks.forEach(callback => {
      try {
        callback(error);
      } catch (err) {
        console.error('Error in error callback:', err);
      }
    });
  }

  /**
   * Notify all status callbacks
   */
  private notifyStatus(connected: boolean): void {
    this.statusCallbacks.forEach(callback => {
      try {
        callback(connected);
      } catch (error) {
        console.error('Error in status callback:', error);
      }
    });
  }

  /**
   * Check if currently connected
   */
  isConnected(): boolean {
    return this.eventSource !== null && this.eventSource.readyState === EventSource.OPEN;
  }
}

// Export singleton instance
export const watcherService = new WatcherService();

