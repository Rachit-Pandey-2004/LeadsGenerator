import { useEffect, useRef, useState } from 'react';

type Status = 'Connected' | 'Disconnected' | 'Error' | 'Connecting';

interface WebSocketMessage {
  query: string;
  status: 'success' | 'error';
  data?: any;
  response?: any;
}

interface UseWebSocketOptions {
  url: string;
  onMessage: (msg: WebSocketMessage) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket({
  url,
  onMessage,
  onOpen,
  onClose,
  onError,
  reconnect = true,
  reconnectInterval = 1000,
  maxReconnectAttempts = 10
}: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeout = useRef<number | null>(null);
  if (reconnectTimeout.current) {
    window.clearTimeout(reconnectTimeout.current);
  }  
  const [status, setStatus] = useState<Status>('Connecting');

  const connect = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      reconnectAttempts.current = 0;
      setStatus('Connected');
      onOpen?.();
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        onMessage(message);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onclose = () => {
      setStatus('Disconnected');
      onClose?.();
      if (reconnect && reconnectAttempts.current < maxReconnectAttempts) {
        scheduleReconnect();
      }
    };

    ws.onerror = (error) => {
      setStatus('Error');
      onError?.(error);
      ws.close(); // force onclose and reconnect
    };
  };

  const scheduleReconnect = () => {
    const delay = Math.min(reconnectInterval * 2 ** reconnectAttempts.current, 30000);
    reconnectTimeout.current = setTimeout(() => {
      reconnectAttempts.current += 1;
      setStatus('Connecting');
      connect();
    }, delay);
  };

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      wsRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

  return {
    send: (data: object) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(data));
      }
    },
    status,
    connected: status === 'Connected',
  };
}