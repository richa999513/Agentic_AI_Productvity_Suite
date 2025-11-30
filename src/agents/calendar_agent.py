"""Calendar Agent for managing events and schedules."""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from src.agents.base_agent import BaseAgent
from src.memory.memory_bank import memory_bank
from src.models.schemas import EventCreate, EventType
from config.logging_config import logger


class CalendarAgent(BaseAgent):
    """Agent responsible for calendar and event management."""
    
    def __init__(self):
        super().__init__(
            name="CalendarAgent",
            description="Manages calendar events, meetings, and schedules"
        )
    
    async def process(self, user_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process calendar management requests."""
        action = input_data.get("action", "list")
        
        if action == "create":
            return await self._create_event(user_id, input_data)
        elif action == "list":
            return await self._list_events(user_id, input_data)
        elif action == "find_slot":
            return await self._find_free_slot(user_id, input_data)
        elif action == "check_conflicts":
            return await self._check_conflicts(user_id, input_data)
        elif action == "suggest_schedule":
            return await self._suggest_schedule(user_id)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _create_event(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event."""
        title = data.get("title")
        start_time_str = data.get("start_time")
        end_time_str = data.get("end_time")
        
        # Parse times
        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str) if end_time_str else start_time + timedelta(hours=1)
        except:
            return {"error": "Invalid time format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}
        
        # Check for conflicts
        conflicts = await self._check_time_conflicts(user_id, start_time, end_time)
        if conflicts:
            return {
                "warning": "Time conflict detected",
                "conflicts": conflicts,
                "suggestion": "Consider rescheduling or shortening the event"
            }
        
        # Create event
        event = memory_bank.create_event(
            user_id=user_id,
            title=title,
            description=data.get("description", ""),
            start_time=start_time,
            end_time=end_time,
            event_type=EventType(data.get("event_type", "meeting")),
            location=data.get("location"),
            attendees=data.get("attendees", [])
        )
        
        return {
            "event_id": event.event_id,
            "title": event.title,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "message": f"Event created: {event.title}"
        }
    
    async def _list_events(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """List events for a user."""
        days = data.get("days", 7)
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days)
        
        events = memory_bank.get_events(user_id, start_date, end_date)
        
        # Group by date
        events_by_date = {}
        for event in events:
            date_key = event.start_time.date().isoformat()
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            
            events_by_date[date_key].append({
                "event_id": event.event_id,
                "title": event.title,
                "start_time": event.start_time.strftime("%H:%M"),
                "end_time": event.end_time.strftime("%H:%M"),
                "type": event.event_type.value,
                "location": event.location
            })
        
        return {
            "total": len(events),
            "events_by_date": events_by_date,
            "message": f"Found {len(events)} events in the next {days} days"
        }
    
    async def _find_free_slot(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Find free time slots."""
        duration_minutes = data.get("duration", 60)
        days_ahead = data.get("days_ahead", 7)
        
        start_date = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=days_ahead)
        
        # Get existing events
        events = memory_bank.get_events(user_id, start_date, end_date)
        
        # Find free slots
        free_slots = []
        current = start_date
        
        while current < end_date and len(free_slots) < 5:
            # Skip weekends (optional)
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                slot_end = current + timedelta(minutes=duration_minutes)
                
                # Check if slot is free
                is_free = True
                for event in events:
                    if (current < event.end_time and slot_end > event.start_time):
                        is_free = False
                        break
                
                if is_free and 9 <= current.hour < 17:  # Work hours
                    free_slots.append({
                        "start": current.isoformat(),
                        "end": slot_end.isoformat(),
                        "date": current.date().isoformat(),
                        "time": current.strftime("%H:%M")
                    })
            
            current += timedelta(minutes=30)
        
        return {
            "duration_minutes": duration_minutes,
            "free_slots": free_slots,
            "message": f"Found {len(free_slots)} available slots"
        }
    
    async def _check_conflicts(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for scheduling conflicts."""
        start_time = datetime.fromisoformat(data.get("start_time"))
        end_time = datetime.fromisoformat(data.get("end_time"))
        
        conflicts = await self._check_time_conflicts(user_id, start_time, end_time)
        
        return {
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts,
            "message": f"Found {len(conflicts)} conflicts" if conflicts else "No conflicts"
        }
    
    async def _check_time_conflicts(self, user_id: str, start_time: datetime, 
                                   end_time: datetime) -> List[Dict[str, Any]]:
        """Helper to check for time conflicts."""
        # Get events in the time range
        search_start = start_time - timedelta(hours=1)
        search_end = end_time + timedelta(hours=1)
        
        events = memory_bank.get_events(user_id, search_start, search_end)
        
        conflicts = []
        for event in events:
            if start_time < event.end_time and end_time > event.start_time:
                conflicts.append({
                    "event_id": event.event_id,
                    "title": event.title,
                    "start": event.start_time.isoformat(),
                    "end": event.end_time.isoformat()
                })
        
        return conflicts
    
    async def _suggest_schedule(self, user_id: str) -> Dict[str, Any]:
        """Suggest an optimal daily schedule using AI."""
        # Get today's events
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        events = memory_bank.get_events(user_id, today_start, today_end)
        
        # Get tasks
        from src.models.schemas import TaskStatus
        tasks = memory_bank.get_tasks(user_id, status=TaskStatus.TODO)
        
        # Build prompt for AI
        event_list = "\n".join([
            f"- {e.title} ({e.start_time.strftime('%H:%M')} - {e.end_time.strftime('%H:%M')})"
            for e in events
        ])
        
        task_list = "\n".join([
            f"- {t.title} (Priority: {t.priority.value})"
            for t in tasks[:5]
        ])
        
        prompt = f"""Create an optimal schedule for today considering:

Events already scheduled:
{event_list or "No events scheduled"}

Pending tasks:
{task_list or "No pending tasks"}

Suggest time blocks for:
1. Focus work on high-priority tasks
2. Breaks and rest
3. Task completion
4. Meeting preparation

Consider work hours: 9 AM - 5 PM"""
        
        suggestion = await self.call_llm(prompt)
        
        return {
            "events_count": len(events),
            "tasks_count": len(tasks),
            "schedule_suggestion": suggestion
        }


# Global instance
calendar_agent = CalendarAgent()