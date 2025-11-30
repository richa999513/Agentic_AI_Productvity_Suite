"""Analytics agent — provides summaries and reports."""
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from config.logging_config import logger
from src.memory.memory_bank import memory_bank


class AnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AnalyticsAgent", description="Provides analytics and reports for users")

    async def process(self, user_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action")
        if action == "daily_summary":
            tasks = memory_bank.get_tasks(user_id)
            completed = [t for t in tasks if getattr(t, "status", None) and getattr(t.status, 'value', None) == 'completed']
            summary_text = f"Today: {len(completed)} of {len(tasks)} tasks completed."
            return {"summary": summary_text, "total_tasks": len(tasks), "completed_tasks": len(completed)}
        elif action == "weekly_report":
            tasks = memory_bank.get_tasks(user_id) # Potentially filter by last 7 days here
            report_text = f"This week: {len(tasks)} tasks tracked. Further weekly breakdown to be implemented."
            return {"report": report_text, "total_tasks_week": len(tasks)}
        else:
            return {"message": "Unknown analytics action"}


analytics_agent = AnalyticsAgent()