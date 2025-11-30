# config/__init__.py
"""Configuration package."""
from config.settings import settings
from config.logging_config import logger

__all__ = ['settings', 'logger']


# src/__init__.py
"""Main source package."""


# src/agents/__init__.py
"""Agents package."""
from src.agents.base_agent import BaseAgent
from src.agents.task_manager_agent import task_manager_agent

__all__ = ['BaseAgent', 'task_manager_agent']


# src/tools/__init__.py
"""Tools package."""
from src.tools.google_search_tool import google_search_tool
from src.tools.code_execution_tool import code_execution_tool

__all__ = ['google_search_tool', 'code_execution_tool']


# src/memory/__init__.py
"""Memory management package."""
from src.memory.session_manager import session_manager
from src.memory.memory_bank import memory_bank

__all__ = ['session_manager', 'memory_bank']


# src/models/__init__.py
"""Data models package."""
from src.models.database import (
    Base, UserDB, TaskDB, CalendarEventDB, 
    EmailDB, NoteDB, ProductivityMetricsDB
)
from src.models.schemas import (
    Task, TaskCreate, TaskUpdate, TaskPriority, TaskStatus,
    CalendarEvent, EventCreate, EventType,
    Email, EmailCreate,
    Note, NoteCreate,
    AgentResponse, AgentMessage
)

__all__ = [
    'Base', 'UserDB', 'TaskDB', 'CalendarEventDB', 
    'EmailDB', 'NoteDB', 'ProductivityMetricsDB',
    'Task', 'TaskCreate', 'TaskUpdate', 'TaskPriority', 'TaskStatus',
    'CalendarEvent', 'EventCreate', 'EventType',
    'Email', 'EmailCreate',
    'Note', 'NoteCreate',
    'AgentResponse', 'AgentMessage'
]


# tests/__init__.py
"""Tests package."""


# scripts/__init__.py
"""Scripts package."""