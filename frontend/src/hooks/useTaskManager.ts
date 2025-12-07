import { useState } from 'react';
import { optimizeTask as apiOptimizeTask, runAgent as apiRunAgent, stopAgent as apiStopAgent } from '../api';
import type { OptimizedPrompt } from '../types';

export const useTaskManager = (refreshHistory: () => void) => {
  const [task, setTask] = useState('');
  const [optimizedData, setOptimizedData] = useState<OptimizedPrompt | null>(null);
  const [loading, setLoading] = useState(false);

  const optimizeTask = async () => {
    setLoading(true);
    try {
      const data = await apiOptimizeTask(task);
      setOptimizedData(data);
      refreshHistory(); // Update history list after optimization
    } catch (err) {
      console.error("Error optimizing task:", err);
    }
    setLoading(false);
  };

  const runAgent = async () => {
    if (!optimizedData || !optimizedData.id) {
        console.error("No optimized data or task ID to run agent.");
        return;
    }
    try {
      await apiRunAgent(optimizedData.id);
      // Status update comes via WS and is handled by useAppStatus
    } catch (err) {
      console.error("Error running agent:", err);
    }
  };

  const stopAgent = async () => {
    try {
      await apiStopAgent();
    } catch (err) {
      console.error("Error stopping agent:", err);
    }
  };

  return {
    task,
    setTask,
    optimizedData,
    setOptimizedData,
    loading,
    optimizeTask,
    runAgent,
    stopAgent,
  };
};
