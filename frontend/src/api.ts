import type { OptimizedPrompt, TaskHistory, RunRequest } from './types';

const API_BASE = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/api/ws';

export const getWsUrl = () => WS_URL;

export const fetchStatus = async (): Promise<{ status: string }> => {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
};

export const fetchHistory = async (): Promise<TaskHistory[]> => {
  const res = await fetch(`${API_BASE}/history`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
};

export const optimizeTask = async (description: string): Promise<OptimizedPrompt> => {
  const res = await fetch(`${API_BASE}/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ description, context_files: [] }),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
};

export const runAgent = async (taskId: number): Promise<{ status: string; message: string; task_id: number }> => {
  const payload: RunRequest = { task_id: taskId };
  const res = await fetch(`${API_BASE}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
};

export const stopAgent = async (): Promise<{ status: string }> => {
  const res = await fetch(`${API_BASE}/stop`, { method: 'POST' });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
};
