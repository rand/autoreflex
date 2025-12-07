import asyncio
import os
import sys
from datetime import datetime
from app.core.websockets import manager
from app.database import SessionLocal, Run, Log

class AgentActor:
    def __init__(self):
        self.process = None
        self.status = "idle"
        self.current_run_id = None

    async def start_task(self, prompt: str, task_id: int):
        if self.status == "running":
            raise Exception("Agent is already running")

        self.status = "running"
        await manager.broadcast({"type": "status", "data": "running"})
        
        # Create Run record
        db = SessionLocal()
        try:
            run = Run(task_id=task_id, status="running")
            db.add(run)
            db.commit()
            db.refresh(run)
            self.current_run_id = run.id
        finally:
            db.close()

        # Start Subprocess
        # We use sys.executable to ensure we use the same python environment
        cmd = [sys.executable, "app/core/simulator.py", "--prompt", prompt]
        
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        asyncio.create_task(self._monitor_process())

    async def stop_task(self):
        if self.process and self.process.returncode is None:
            self.process.terminate()
            try:
                await self.process.wait()
            except ProcessLookupError:
                pass
        
        self.status = "idle"
        await manager.broadcast({"type": "status", "data": "idle"})
        
        # Update Run record if exists
        if self.current_run_id:
            db = SessionLocal()
            try:
                run = db.query(Run).filter(Run.id == self.current_run_id).first()
                if run:
                    run.status = "cancelled"
                    run.end_time = datetime.utcnow()
                    db.commit()
                    
                    # Log cancellation
                    log = Log(run_id=run.id, level="WARN", message="Task Manually Stopped")
                    db.add(log)
                    db.commit()
            finally:
                db.close()

    async def _monitor_process(self):
        if not self.process:
            return

        # Read stdout line by line
        # We catch exceptions to ensure we don't crash the loop
        try:
            async for line in self.process.stdout:
                if line:
                    decoded_line = line.decode().strip()
                    if decoded_line:
                        self._log_to_db(decoded_line)
        except Exception as e:
            print(f"Error reading subprocess stdout: {e}")

        await self.process.wait()
        exit_code = self.process.returncode
        
        # Update Run completion
        db = SessionLocal()
        try:
            run = db.query(Run).filter(Run.id == self.current_run_id).first()
            if run:
                run.status = "completed" if exit_code == 0 else "failed"
                run.end_time = datetime.utcnow()
                run.exit_code = exit_code
                db.commit()
        finally:
            db.close()

        self.status = "idle"
        await manager.broadcast({"type": "status", "data": "idle"})
        self.current_run_id = None

    def _log_to_db(self, message: str, level: str = "INFO"):
        if not self.current_run_id:
            return
        
        db = SessionLocal()
        try:
            log = Log(run_id=self.current_run_id, message=message, level=level)
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"Failed to write log to DB: {e}")
        finally:
            db.close()

actor = AgentActor()