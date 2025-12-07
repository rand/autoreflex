import asyncio
from sqlalchemy import func
from app.database import SessionLocal, Log
from app.core.websockets import manager

class LogWatcher:
    def __init__(self):
        self.is_running = False
        self.last_log_id = 0
        self._task = None

    async def start(self):
        if self.is_running:
            return

        self.is_running = True
        
        # Initialize last_log_id to avoid replaying old logs on restart
        db = SessionLocal()
        try:
            max_id = db.query(func.max(Log.id)).scalar()
            self.last_log_id = max_id if max_id else 0
        finally:
            db.close()

        print(f"Observer started. Watching for logs > {self.last_log_id}")
        self._task = asyncio.create_task(self._poll_loop())

    async def stop(self):
        self.is_running = False
        if self._task:
            await self._task
            self._task = None

    async def _poll_loop(self):
        while self.is_running:
            await self._check_logs()
            await asyncio.sleep(0.5)

    async def _check_logs(self):
        db = SessionLocal()
        try:
            # Fetch new logs
            logs = db.query(Log).filter(Log.id > self.last_log_id).order_by(Log.id).all()
            
            for log in logs:
                entry = {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "message": log.message,
                    "source": log.source
                }
                await manager.broadcast({"type": "log", "data": entry})
                self.last_log_id = log.id
        except Exception as e:
            print(f"Observer error: {e}")
        finally:
            db.close()

# Default watcher instance
watcher = LogWatcher()