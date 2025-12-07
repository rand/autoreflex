import { useEffect, useState } from 'react';
import { fetchHistory } from '../api';
import type { TaskHistory } from '../types';

export const useHistory = () => {
  const [history, setHistory] = useState<TaskHistory[]>([]);

  const refreshHistory = async () => {
      try {
          const data = await fetchHistory();
          setHistory(data);
      } catch (e) { console.error("Failed to fetch history:", e) }
  };

  useEffect(() => {
    refreshHistory();
  }, []);

  return { history, refreshHistory };
};
