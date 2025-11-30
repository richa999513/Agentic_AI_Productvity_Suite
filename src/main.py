"""Main FastAPI application - Complete version with all agents."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, EmailStr, ValidationError
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from config.logging_config import logger
from src.agents.task_manager_agent import task_manager_agent
from src.agents.calendar_agent import calendar_agent
from src.agents.email_agent import email_agent
from src.agents.note_agent import note_agent
from src.agents.analytics_agent import analytics_agent
from src.memory.memory_bank import memory_bank
from src.memory.session_manager import session_manager
from src.orchestration.agent_orchestrator import agent_orchestrator
from src.models.schemas import UserCreate, TaskCreate, TaskUpdate, EventCreate, EmailCreate, NoteCreate # Add EventCreate and other models needed

# Initialize FastAPI app (disable automatic docs)
app = FastAPI(
    title="AI Personal Productivity Suite",
    description="Multi-agent system for personal productivity management",
    version="1.0.0",
    docs_url="/api/docs",  # Move docs to /api/docs instead of /docs
    openapi_url="/api/openapi.json"  # Move OpenAPI schema to /api/openapi.json
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve index.html for root path
@app.get("/", include_in_schema=False)
async def root():
    """Serve the main UI."""
    index_path = Path(__file__).parent.parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    return {"message": "Welcome to AI Productivity Workspace. Visit /api/docs for API documentation."}

# Mount static files (must be after root route)
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Request/Response Models
class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None


class AgentRequest(BaseModel):
    user_id: str
    action: str
    data: Optional[Dict[str, Any]] = {}


class WorkflowRequest(BaseModel):
    user_id: str
    workflow_type: str
    params: Optional[Dict[str, Any]] = {}

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# User endpoints
@app.post("/api/users/create")
async def create_user(body: UserCreate):
    """Create a new user from JSON body."""
    try:
        print(f"Received user creation request: {body.dict()}")
        user = memory_bank.create_user(name=body.name, email=body.email)
        return {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "message": "User created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """Get user information."""
    user = memory_bank.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "timezone": user.timezone,
        "preferences": user.preferences
    }


# Main chat interface
@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Simple chat fallback: echo the message if assistant not configured."""
    try:
        # If there is a user_assistant_agent defined elsewhere, call it.
        if "user_assistant_agent" in globals():
            result = await globals()["user_assistant_agent"].execute(
                user_id=request.user_id,
                input_data={"message": request.message}
            )
            if result.get("success"):
                response_text = result.get("data", {}).get("response", "")
                session_manager.update_context(request.user_id, request.message, response_text)
            return result

        # Otherwise return a simple echo response so UI doesn't fail.
        response_text = f"Echo: {request.message}"
        session_manager.update_context(request.user_id, request.message, response_text)
        return {"success": True, "data": {"response": response_text}}
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Task endpoints
@app.post("/api/tasks/create/{user_id}")
async def create_task(user_id: str, body: TaskCreate):
    """Create a task for a user (UI-friendly)."""
    try:
        # Convert priority/status to enums where memory_bank expects them
        task = memory_bank.create_task(
            user_id=user_id,
            title=body.title,
            description=body.description or "",
            priority=body.priority,
            due_date=body.due_date
        )
        return {"success": True, "task_id": task.task_id}
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/tasks/update/{task_id}")
async def update_task(task_id: str, body: TaskUpdate):
    print(f"DEBUG: Received task update request for task {task_id}: {body.dict()}")
    try:
        updates = {k: v for k, v in body.dict().items() if v is not None}
        task = memory_bank.update_task(task_id, **updates)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"success": True, "task_id": task.task_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    try:
        ok = memory_bank.delete_task(task_id)
        return {"success": ok}
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{user_id}")
async def get_tasks(user_id: str, status: Optional[str] = None):
    """Return tasks for UI in a simple list format."""
    try:
        db_tasks = memory_bank.get_tasks(user_id, status=status)
        tasks = []
        for t in db_tasks:
            tasks.append({
                "task_id": t.task_id,
                "user_id": t.user_id,
                "title": t.title,
                "description": t.description,
                "priority": str(t.priority.value) if hasattr(t.priority, 'value') else str(t.priority),
                "status": str(t.status.value) if hasattr(t.status, 'value') else str(t.status),
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "tags": t.tags or [],
                "created_at": t.created_at.isoformat() if t.created_at else None
            })
        return {"tasks": tasks}
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Calendar endpoints
@app.post("/api/calendar/create/{user_id}")
async def create_event(user_id: str, body: EventCreate):
    """Create a calendar event for a user (UI-friendly)."""
    try:
        event = memory_bank.create_event(
            user_id=user_id,
            title=body.title,
            description=body.description or "",
            start_time=body.start_time,
            end_time=body.end_time,
            event_type=body.event_type,
            location=body.location,
            attendees=body.attendees
        )
        return {"success": True, "event_id": event.event_id}
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/calendar/{event_id}")
async def delete_event(event_id: str):
    try:
        ok = memory_bank.delete_event(event_id)
        return {"success": ok}
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calendar")
async def manage_calendar(request: AgentRequest):
    """Manage calendar events (via AgentRequest for other actions)."""
    try:
        action = request.action
        # Fallback to agent for actions (e.g., find_slot, check_conflicts, suggest_schedule)
        result = await calendar_agent.execute(
            user_id=request.user_id,
            input_data={"action": request.action, **request.data}
        )
        return result
    except Exception as e:
        logger.error(f"Error managing calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calendar/{user_id}")
async def get_events(user_id: str, days: int = 7):
    """Get calendar events."""
    try:
        # Return simple list for UI
        events = memory_bank.get_events(user_id, days=days)
        evs = []
        for e in events:
            evs.append({
                "event_id": e.event_id,
                "title": e.title,
                "description": e.description,
                "start_time": e.start_time.isoformat() if e.start_time else None,
                "end_time": e.end_time.isoformat() if e.end_time else None,
                "event_type": str(e.event_type.name) if hasattr(e.event_type, 'name') else str(e.event_type)
            })
        return {"events": evs}
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Email endpoints
@app.post("/api/emails/send/{user_id}")
async def send_email(user_id: str, body: EmailCreate):
    """Send an email for a user (UI-friendly)."""
    try:
        # The 'from' address can be a default or fetched from user settings
        user = memory_bank.get_user(user_id)
        if not user or not user.email:
            logger.error(f"User email not found for sending for user {user_id}")
            raise HTTPException(status_code=400, detail="User email not found for sending")

        email = memory_bank.create_email(
            user_id=user_id,
            from_address=user.email,
            to_addresses=body.to,
            subject=body.subject,
            body=body.body
        )
        return {"success": True, "email_id": email.email_id, "message": "Email sent successfully"}
    except ValidationError as e:
        logger.error(f"Pydantic validation error in send_email for user {user_id}: {e.errors()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except HTTPException as e:
        logger.error(f"HTTP Exception in send_email for user {user_id}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails/{user_id}")
async def get_emails(user_id: str):
    """Get emails for a user."""
    try:
        db_emails = memory_bank.get_emails(user_id)
        emails = []
        for e in db_emails:
            emails.append({
                "email_id": e.email_id,
                "user_id": e.user_id,
                "from_address": e.from_address,
                "to_addresses": e.to_addresses,
                "subject": e.subject,
                "body": e.body,
                "received_at": e.received_at.isoformat()
            })
        return {"emails": emails}
    except Exception as e:
        logger.error(f"Error getting emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/emails/{email_id}")
async def delete_email(email_id: str):
    """Delete an email."""
    try:
        ok = memory_bank.delete_email(email_id)
        return {"success": ok, "message": "Email deleted successfully" if ok else "Email not found"}
    except Exception as e:
        logger.error(f"Error deleting email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/email")
async def manage_email(request: AgentRequest):
    """Manage emails (via AgentRequest for other actions)."""
    try:
        action = request.action
        # Fallback to agent for actions other than create, list, delete
        result = await email_agent.execute(user_id=request.user_id, input_data={"action": action, **request.data})
        return result
    except Exception as e:
        logger.error(f"Error managing email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Note endpoints
@app.post("/api/notes/create/{user_id}")
async def create_note(user_id: str, body: NoteCreate):
    """Create a note for a user (UI-friendly)."""
    try:
        note = memory_bank.create_note(
            user_id=user_id,
            title=body.title,
            content=body.content
        )
        return {"success": True, "note_id": note.note_id, "message": "Note created successfully"}
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notes/{user_id}")
async def get_notes(user_id: str):
    """Get notes for a user."""
    try:
        db_notes = memory_bank.get_notes(user_id)
        notes = []
        for n in db_notes:
            notes.append({
                "note_id": n.note_id,
                "user_id": n.user_id,
                "title": n.title,
                "content": n.content,
                "created_at": n.created_at.isoformat()
            })
        return {"notes": notes}
    except Exception as e:
        logger.error(f"Error getting notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete a note."""
    try:
        ok = memory_bank.delete_note(note_id)
        return {"success": ok, "message": "Note deleted successfully" if ok else "Note not found"}
    except Exception as e:
        logger.error(f"Error deleting note: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notes")
async def manage_note(request: AgentRequest):
    """Manage notes (via AgentRequest for search or other agent actions)."""
    try:
        action = request.action
        if action == 'search':
            result = await note_agent.execute(
                user_id=request.user_id,
                input_data={"action": "search", "query": request.data.get('query', '')}
            )
            return result
        else:
            # fallback to agent for other actions
            result = await note_agent.execute(user_id=request.user_id, input_data={"action": action, **request.data})
            return result
    except Exception as e:
        logger.error(f"Error managing note: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notes/search/{user_id}")
async def search_notes(user_id: str, q: str):
    """Search notes."""
    try:
        result = await note_agent.execute(
            user_id=user_id,
            input_data={"action": "search", "query": q}
        )
        return result
    except Exception as e:
        logger.error(f"Error searching notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Analytics endpoints
@app.get("/api/analytics/{user_id}/summary")
async def get_daily_summary(user_id: str):
    """Get daily summary."""
    try:
        result = await analytics_agent.execute(
            user_id=user_id,
            input_data={"action": "daily_summary"}
        )
        return result
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/{user_id}/weekly")
async def get_weekly_report(user_id: str):
    """Get weekly report."""
    try:
        result = await analytics_agent.execute(
            user_id=user_id,
            input_data={"action": "weekly_report"}
        )
        return result
    except Exception as e:
        logger.error(f"Error getting weekly report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/{user_id}/score")
async def get_productivity_score(user_id: str):
    """Get productivity score."""
    try:
        result = await analytics_agent.execute(
            user_id=user_id,
            input_data={"action": "productivity_score"}
        )
        return result
    except Exception as e:
        logger.error(f"Error getting score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Workflow endpoints
@app.post("/api/workflows/morning-routine")
async def morning_routine(user_id: str):
    """Execute morning routine workflow."""
    try:
        result = await agent_orchestrator.execute_morning_routine(user_id)
        return result
    except Exception as e:
        logger.error(f"Error in morning routine: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workflows/weekly-review")
async def weekly_review(user_id: str):
    """Execute weekly review workflow."""
    try:
        result = await agent_orchestrator.execute_weekly_review(user_id)
        return result
    except Exception as e:
        logger.error(f"Error in weekly review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workflows/custom")
async def custom_workflow(request: WorkflowRequest):
    """Execute custom workflow."""
    try:
        workflow_type = request.workflow_type
        
        if workflow_type == "sequential":
            result = await agent_orchestrator.execute_sequential(
                request.user_id,
                request.params.get("workflow", [])
            )
        elif workflow_type == "parallel":
            result = await agent_orchestrator.execute_parallel(
                request.user_id,
                request.params.get("tasks", [])
            )
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        return result
    except Exception as e:
        logger.error(f"Error in custom workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Session endpoints
@app.get("/api/session/{user_id}")
async def get_session(user_id: str):
    """Get user session data."""
    context = session_manager.get_context(user_id)
    return {
        "user_id": user_id,
        "conversation_history": context
    }


@app.delete("/api/session/{user_id}")
async def clear_session(user_id: str):
    """Clear user session."""
    success = session_manager.clear_user_sessions(user_id)
    return {"success": success, "message": "Session cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )