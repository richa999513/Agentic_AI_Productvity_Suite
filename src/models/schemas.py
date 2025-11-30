"""Pydantic schemas for data validation."""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventType(str, Enum):
    MEETING = "meeting"
    REMINDER = "reminder"
    DEADLINE = "deadline"
    PERSONAL = "personal"


# User Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserProfile(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    timezone: str = "UTC"
    work_hours_start: str = "09:00"
    work_hours_end: str = "17:00"
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Task Schemas
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    estimated_duration: Optional[int] = None  # minutes


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    completed_at: Optional[datetime] = None


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: str
    user_id: str
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[datetime]
    tags: List[str]
    estimated_duration: Optional[int]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


# Calendar Event Schemas
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    event_type: EventType = EventType.MEETING
    location: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)


class CalendarEvent(BaseModel):
    event_id: str
    user_id: str
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    event_type: EventType
    location: Optional[str]
    attendees: List[str]
    created_at: datetime


# Email Schemas
class EmailCreate(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = Field(default_factory=list)
    attachments: Optional[List[str]] = Field(default_factory=list)


class Email(BaseModel):
    email_id: str
    user_id: str
    from_address: EmailStr
    to_addresses: List[EmailStr]
    subject: str
    body: str
    received_at: datetime
    is_read: bool = False
    labels: List[str] = Field(default_factory=list)


# Note Schemas
class NoteCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = Field(default_factory=list)


class Note(BaseModel):
    note_id: str
    user_id: str
    title: str
    content: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime


# Agent Message Schemas
class AgentMessage(BaseModel):
    msg_id: str
    from_agent: str
    to_agent: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Analytics Schemas
class ProductivityMetrics(BaseModel):
    user_id: str
    date: datetime
    tasks_completed: int
    tasks_created: int
    meetings_attended: int
    focus_time_minutes: int
    productivity_score: float


# API Response Schemas
class AgentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    agent: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)