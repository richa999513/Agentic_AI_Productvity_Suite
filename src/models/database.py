"""Database models using SQLAlchemy."""
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid
from src.models.schemas import TaskPriority, TaskStatus, EventType

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class UserDB(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    timezone = Column(String(50), default="UTC")
    work_hours_start = Column(String(5), default="09:00")
    work_hours_end = Column(String(5), default="17:00")
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = relationship("TaskDB", back_populates="user", cascade="all, delete-orphan")
    events = relationship("CalendarEventDB", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("NoteDB", back_populates="user", cascade="all, delete-orphan")


class TaskDB(Base):
    __tablename__ = "tasks"
    
    task_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO)
    due_date = Column(DateTime)
    tags = Column(JSON, default=list)
    estimated_duration = Column(Integer)  # minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("UserDB", back_populates="tasks")


class CalendarEventDB(Base):
    __tablename__ = "calendar_events"
    
    event_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    event_type = Column(SQLEnum(EventType), default=EventType.MEETING)
    location = Column(String(255))
    attendees = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserDB", back_populates="events")


class EmailDB(Base):
    __tablename__ = "emails"
    
    email_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    from_address = Column(String(255), nullable=False)
    to_addresses = Column(JSON, nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text)
    received_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    labels = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class NoteDB(Base):
    __tablename__ = "notes"
    
    note_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserDB", back_populates="notes")


class ProductivityMetricsDB(Base):
    __tablename__ = "productivity_metrics"
    
    metric_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    date = Column(DateTime, nullable=False)
    tasks_completed = Column(Integer, default=0)
    tasks_created = Column(Integer, default=0)
    meetings_attended = Column(Integer, default=0)
    focus_time_minutes = Column(Integer, default=0)
    productivity_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class AgentLogDB(Base):
    __tablename__ = "agent_logs"
    
    log_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"))
    agent_name = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    status = Column(String(50), nullable=False)
    execution_time_ms = Column(Float)
    error_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)