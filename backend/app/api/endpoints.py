from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import List, cast

from app.models.schemas import TaskRequest, OptimizedPrompt, LogEntry, RunRequest
from app.core.optimizer import optimizer
from app.core.actor import actor
from app.core.observer import watcher
from app.core.websockets import manager
from app.database import SessionLocal, Task, Optimization, Run, engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.on_event("startup")
async def startup_event():
    await watcher.start()

@router.on_event("shutdown")
async def shutdown_event():
    await watcher.stop()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for client pings if needed
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/optimize", response_model=OptimizedPrompt)
async def optimize_task(task: TaskRequest, db: Session = Depends(get_db)):
    # Persist task
    db_task = Task(description=task.description, status="optimizing")
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    optimized = await optimizer.optimize(task)
    
    # Persist optimization
    db_opt = Optimization(
        task_id=db_task.id,
        original_prompt=optimized.original_task,
        optimized_prompt=optimized.optimized_prompt,
        reasoning=optimized.reasoning
    )
    db.add(db_opt)
    db.commit()

    # Hack: Attach ID for the frontend to use in run
    optimized.id = cast(int, db_task.id) 
    return optimized

@router.post("/run")
async def run_agent(request: RunRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task_id = request.task_id
    
    # Fetch optimization to get the prompt
    # We assume strict flow: Optimize -> Run
    optimization = db.query(Optimization).filter(Optimization.task_id == task_id).first()
    
    if not optimization:
        raise HTTPException(status_code=404, detail="Optimization not found for this task. Please optimize first.")
    
    try:
        await actor.start_task(cast(str, optimization.optimized_prompt), task_id)
        return {"status": "started", "message": "Agent loop initiated.", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/stop")
async def stop_agent():
    await actor.stop_task()
    return {"status": "stopped"}

@router.get("/status")
async def get_status():
    return {"status": actor.status}

@router.get("/history")
async def get_history(db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.created_at.desc()).limit(20).all()
    return tasks
