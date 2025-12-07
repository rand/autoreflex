from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime, timezone
from typing import Any
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base: Any = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending, optimizing, running, completed, failed
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    # One-to-One
    optimization = relationship("Optimization", back_populates="task", uselist=False)
    runs = relationship("Run", back_populates="task")

class Optimization(Base):
    __tablename__ = "optimizations"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    original_prompt = Column(Text)
    optimized_prompt = Column(Text)
    reasoning = Column(Text)
    
    task = relationship("Task", back_populates="optimization")

class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    start_time = Column(DateTime, default=utc_now)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="running")
    exit_code = Column(Integer, nullable=True)
    
    logs = relationship("Log", back_populates="run")
    task = relationship("Task", back_populates="runs")

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"))
    timestamp = Column(DateTime, default=utc_now)
    level = Column(String, default="INFO")
    message = Column(Text)
    source = Column(String, default="system")

    run = relationship("Run", back_populates="logs")
