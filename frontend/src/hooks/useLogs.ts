import { useEffect, useRef, useState } from 'react';
import { getWsUrl } from '../api';
import type { LogEntry } from '../types';

export const useLogs = (setStatus: (s: string) => void) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // WebSocket for Real-time Logs
  useEffect(() => {
    const ws = new WebSocket(getWsUrl());

    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === 'log') {
        setLogs((prev) => [...prev, payload.data].slice(-500)); // Keep last 500
      } else if (payload.type === 'status') {
        setStatus(payload.data); // Update status via the provided setter
      }
    };

    return () => ws.close();
  }, [setStatus]); // Dependency array for useEffect

  // Auto-scroll logs
  useEffect(() => {
    if (logsEndRef.current) {
        logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  return { logs, logsEndRef };
};
