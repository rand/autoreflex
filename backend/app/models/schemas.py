from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class TaskRequest(BaseModel):
    description: str = Field(..., description="The natural language description of the coding task")
    context_files: List[str] = Field(default=[], description="List of file paths relevant to the task")
    constraints: Optional[str] = Field(None, description="Specific constraints or guidelines")

class OptimizedPrompt(BaseModel):
    id: Optional[int] = None
    original_task: str
    optimized_prompt: str
    reasoning: str
    estimated_tokens: int

class RunRequest(BaseModel):
    task_id: int = Field(..., description="The ID of the task to run")

class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    message: str
    source: str = "claude-cli"