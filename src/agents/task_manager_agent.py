"""Task Manager Agent for handling task operations."""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from src.agents.base_agent import BaseAgent
from src.memory.memory_bank import memory_bank
from src.models.schemas import TaskCreate, TaskPriority, TaskStatus
from config.logging_config import logger

# Lazy import to avoid huggingface_hub version conflicts
vector_store = None


def _get_vector_store():
    """Lazy load vector store on first use."""
    global vector_store
    if vector_store is None:
        try:
            from src.memory.vector_store import vector_store as vs
            vector_store = vs
        except Exception as e:
            logger.warning(f"Vector store unavailable: {e}")
            vector_store = None
    return vector_store

class TaskManagerAgent(BaseAgent):
    """Agent responsible for task management operations."""
    
    def __init__(self):
        super().__init__(
            name="TaskManager",
            description="Manages tasks, priorities, and deadlines for users"
        )
    
    async def process(self, user_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process task management requests."""
        action = input_data.get("action", "list")
        
        if action == "create":
            return await self._create_task(user_id, input_data)
        elif action == "list":
            return await self._list_tasks(user_id, input_data)
        elif action == "update":
            return await self._update_task(user_id, input_data)
        elif action == "complete":
            return await self._complete_task(user_id, input_data)
        elif action == "search":
            return await self._search_tasks(user_id, input_data)
        elif action == "suggest":
            return await self._suggest_next_task(user_id)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _create_task(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task."""
        # Extract task data
        title = data.get("title")
        description = data.get("description", "")
        priority = data.get("priority", "medium")
        due_date_str = data.get("due_date")
        tags = data.get("tags", [])
        
        if not title:
            # Use LLM to extract task info from natural language
            user_input = data.get("user_input", "")
            prompt = f"""Extract task information from this user input: "{user_input}"

Provide:
1. Task title (clear and concise)
2. Description (if any details provided)
3. Priority (low/medium/high/urgent) - infer from urgency words
4. Due date (if mentioned, format as YYYY-MM-DD)
5. Tags (relevant categories)

Format your response as:
Title: [title]
Description: [description]
Priority: [priority]
Due Date: [date or "none"]
Tags: [tag1, tag2]"""
            
            response = await self.call_llm(prompt)
            # Parse LLM response (simplified)
            title = self._extract_field(response, "Title")
            description = self._extract_field(response, "Description")
            priority = self._extract_field(response, "Priority", "medium")
        
        # Parse due date
        due_date = None
        if due_date_str and due_date_str != "none":
            try:
                due_date = datetime.fromisoformat(due_date_str)
            except:
                pass
        
        # Create task in database
        task = memory_bank.create_task(
            user_id=user_id,
            title=title,
            description=description,
            priority=TaskPriority(priority.lower()),
            due_date=due_date,
            tags=tags
        )
        
        # Add to vector store for semantic search (if available)
        vs = _get_vector_store()
        if vs:
            vs.add_task(
                task_id=task.task_id,
                user_id=user_id,
                title=title,
                description=description or "",
                metadata={"priority": priority, "tags": tags}
            )
        
        return {
            "task_id": task.task_id,
            "title": task.title,
            "priority": task.priority.value,
            "message": f"Created task: {task.title}"
        }
    
    async def _list_tasks(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """List tasks for a user."""
        status = data.get("status")
        if status:
            status = TaskStatus(status)
        
        tasks = memory_bank.get_tasks(user_id, status=status)
        
        # Group by priority
        grouped_tasks = {
            "urgent": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for task in tasks:
            task_info = {
                "task_id": task.task_id,
                "title": task.title,
                "priority": task.priority.value,
                "status": task.status.value,
                "due_date": task.due_date.isoformat() if task.due_date else None
            }
            grouped_tasks[task.priority.value].append(task_info)
        
        return {
            "total": len(tasks),
            "tasks": grouped_tasks,
            "message": f"Found {len(tasks)} tasks"
        }
    
    async def _update_task(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task."""
        task_id = data.get("task_id")
        updates = {k: v for k, v in data.items() if k != "task_id" and k != "action"}
        
        task = memory_bank.update_task(task_id, **updates)
        
        if task:
            return {
                "task_id": task.task_id,
                "message": "Task updated successfully"
            }
        else:
            return {"message": "Task not found"}
    
    async def _complete_task(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mark a task as completed."""
        task_id = data.get("task_id")
        
        task = memory_bank.update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.utcnow()
        )
        
        if task:
            # Send message to analytics agent
            await self.send_message_to_agent(
                "AnalyticsAgent",
                {
                    "type": "task_completed",
                    "payload": {
                        "user_id": user_id,
                        "task_id": task_id,
                        "completed_at": datetime.utcnow().isoformat()
                    }
                }
            )
            
            return {
                "task_id": task.task_id,
                "message": f"Completed: {task.title}"
            }
        else:
            return {"message": "Task not found"}
    
    async def _search_tasks(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search tasks using semantic search."""
        query = data.get("query", "")
        
        vs = _get_vector_store()
        if not vs:
            return {"query": query, "tasks": [], "message": "Vector store not available"}
        
        results = vs.search_tasks(query, user_id, n_results=5)
        
        tasks = []
        for result in results:
            tasks.append({
                "task_id": result['id'],
                "content": result['document'],
                "relevance": 1 - result['distance'] if result['distance'] else 1.0
            })
        
        return {
            "query": query,
            "tasks": tasks,
            "message": f"Found {len(tasks)} relevant tasks"
        }
    
    async def _suggest_next_task(self, user_id: str) -> Dict[str, Any]:
        """Suggest the next task to work on using AI."""
        # Get current tasks
        tasks = memory_bank.get_tasks(user_id, status=TaskStatus.TODO)
        
        if not tasks:
            return {"message": "No pending tasks"}
        
        # Build context for LLM
        task_list = "\n".join([
            f"- {t.title} (Priority: {t.priority.value}, Due: {t.due_date or 'None'})"
            for t in tasks[:10]
        ])
        
        prompt = f"""Based on these pending tasks, suggest which one the user should work on next:

{task_list}

Consider:
1. Priority level
2. Due dates
3. Estimated effort
4. Dependencies

Provide a brief recommendation with reasoning."""
        
        recommendation = await self.call_llm(prompt)
        
        return {
            "suggestion": recommendation,
            "total_pending": len(tasks)
        }
    
    def _extract_field(self, text: str, field: str, default: str = "") -> str:
        """Extract a field from LLM response."""
        lines = text.split("\n")
        for line in lines:
            if line.startswith(f"{field}:"):
                return line.split(":", 1)[1].strip()
        return default


# Global instance
task_manager_agent = TaskManagerAgent()