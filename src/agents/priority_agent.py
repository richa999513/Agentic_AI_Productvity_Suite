"""Priority agent — analyzes task priorities."""
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from config.logging_config import logger
from src.memory.memory_bank import memory_bank


class PriorityAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="PriorityAgent", description="Analyzes and suggests task priorities")

    async def process(self, user_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action")
        if action == "suggest_priority":
            task_title = input_data.get("task_title", "")
            return {"task_title": task_title, "suggested_priority": "medium", "message": "Priority suggestion"}
        elif action == "reorder":
            return {"message": "Tasks reordered by priority"}
        else:
            return {"message": "Unknown priority action"}


priority_agent = PriorityAgent()