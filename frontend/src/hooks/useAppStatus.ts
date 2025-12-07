import { useEffect, useState } from 'react';
import { fetchStatus } from '../api';

export const useAppStatus = () => {
  const [status, setStatus] = useState('idle');

  useEffect(() => {
    const getStatus = async () => {
      try {
        const data = await fetchStatus();
        setStatus(data.status);
      } catch (e) {
        console.error("Failed to fetch initial status:", e);
        setStatus('error');
      }
    };
    getStatus();
  }, []);

  return { status, setStatus };
};
