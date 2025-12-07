export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  source: string;
}

export interface OptimizedPrompt {
  id?: number;
  original_task: string;
  optimized_prompt: string;
  reasoning: string;
  estimated_tokens: number;
}

export interface TaskHistory {
    id: number;
    description: string;
    status: string;
    created_at: string;
}

export interface RunRequest {
  task_id: number;
}
