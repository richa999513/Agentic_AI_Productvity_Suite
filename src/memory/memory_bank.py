"""Long-term memory / DB access helpers."""
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import settings
from config.logging_config import logger
from src.models.database import Base, UserDB, TaskDB
from src.models.schemas import TaskPriority, TaskStatus
import datetime


# Create engine
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class MemoryBank:
    def __init__(self):
        self.engine = engine

    def get_db(self) -> Session:
        return SessionLocal()

    def create_user(self, name: str, email: str, timezone: str = "UTC", preferences: Optional[Dict] = None):
        db = self.get_db()
        try:
            user = UserDB(name=name, email=email, timezone=timezone, preferences=preferences or {})
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
        finally:
            db.close()

    def get_user(self, user_id: str):
        db = self.get_db()
        try:
            return db.query(UserDB).filter(UserDB.user_id == user_id).first()
        finally:
            db.close()

    def get_user_by_email(self, email: str):
        """Return a user by email if exists, else None."""
        db = self.get_db()
        try:
            return db.query(UserDB).filter(UserDB.email == email).first()
        finally:
            db.close()

    def create_task(self, user_id: str, title: str, description: str = "", priority: TaskPriority = TaskPriority.MEDIUM, due_date: Optional[datetime.datetime] = None, tags: Optional[List[str]] = None):
        db = self.get_db()
        try:
            task = TaskDB(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                tags=tags or [],
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            return task
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating task: {e}")
            raise
        finally:
            db.close()

    def get_tasks(self, user_id: str, status: Optional[TaskStatus] = None) -> List[TaskDB]:
        db = self.get_db()
        try:
            q = db.query(TaskDB).filter(TaskDB.user_id == user_id)
            if status:
                q = q.filter(TaskDB.status == status)
            return q.order_by(TaskDB.created_at.desc()).all()
        finally:
            db.close()

    def update_task(self, task_id: str, **updates) -> Optional[TaskDB]:
        db = self.get_db()
        try:
            task = db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
            if not task:
                return None
            for k, v in updates.items():
                if hasattr(task, k):
                    setattr(task, k, v)
            db.add(task)
            db.commit()
            db.refresh(task)
            return task
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating task: {e}")
            raise
        finally:
            db.close()

    def delete_task(self, task_id: str) -> bool:
        db = self.get_db()
        try:
            task = db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
            if not task:
                return False
            db.delete(task)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting task: {e}")
            raise
        finally:
            db.close()

    # Calendar operations
    def create_event(self, user_id: str, title: str, start_time, end_time, event_type=None, description: str = "", location: str = None, attendees: Optional[list] = None):
        from src.models.database import CalendarEventDB
        db = self.get_db()
        try:
            event = CalendarEventDB(
                user_id=user_id,
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                event_type=event_type,
                location=location,
                attendees=attendees or []
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            return event
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating event: {e}")
            raise
        finally:
            db.close()

    def get_events(self, user_id: str, days: int = 7):
        from src.models.database import CalendarEventDB
        db = self.get_db()
        try:
            q = db.query(CalendarEventDB).filter(CalendarEventDB.user_id == user_id)
            return q.order_by(CalendarEventDB.start_time.asc()).all()
        finally:
            db.close()

    def delete_event(self, event_id: str) -> bool:
        from src.models.database import CalendarEventDB
        db = self.get_db()
        try:
            ev = db.query(CalendarEventDB).filter(CalendarEventDB.event_id == event_id).first()
            if not ev:
                return False
            db.delete(ev)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting event: {e}")
            raise
        finally:
            db.close()

    # Email operations
    def create_email(self, user_id: str, from_address: str, to_addresses: list, subject: str, body: str):
        from src.models.database import EmailDB
        db = self.get_db()
        try:
            email = EmailDB(
                user_id=user_id,
                from_address=from_address,
                to_addresses=to_addresses,
                subject=subject,
                body=body
            )
            db.add(email)
            db.commit()
            db.refresh(email)
            return email
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating email: {e}")
            raise
        finally:
            db.close()

    def get_emails(self, user_id: str):
        from src.models.database import EmailDB
        db = self.get_db()
        try:
            return db.query(EmailDB).filter(EmailDB.user_id == user_id).order_by(EmailDB.received_at.desc()).all()
        finally:
            db.close()

    def delete_email(self, email_id: str) -> bool:
        from src.models.database import EmailDB
        db = self.get_db()
        try:
            item = db.query(EmailDB).filter(EmailDB.email_id == email_id).first()
            if not item:
                return False
            db.delete(item)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting email: {e}")
            raise
        finally:
            db.close()

    # Note operations
    def create_note(self, user_id: str, title: str, content: str):
        from src.models.database import NoteDB
        db = self.get_db()
        try:
            note = NoteDB(user_id=user_id, title=title, content=content)
            db.add(note)
            db.commit()
            db.refresh(note)
            return note
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating note: {e}")
            raise
        finally:
            db.close()

    def get_notes(self, user_id: str):
        from src.models.database import NoteDB
        db = self.get_db()
        try:
            return db.query(NoteDB).filter(NoteDB.user_id == user_id).order_by(NoteDB.created_at.desc()).all()
        finally:
            db.close()

    def delete_note(self, note_id: str) -> bool:
        from src.models.database import NoteDB
        db = self.get_db()
        try:
            item = db.query(NoteDB).filter(NoteDB.note_id == note_id).first()
            if not item:
                return False
            db.delete(item)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting note: {e}")
            raise
        finally:
            db.close()


# Global instance
memory_bank = MemoryBank()