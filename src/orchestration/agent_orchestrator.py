"""Agent Orchestrator for coordinating multi-agent workflows."""
from typing import Dict, Any, List
import asyncio
from datetime import datetime
from config.logging_config import logger
from src.agents.task_manager_agent import task_manager_agent
from src.agents.calendar_agent import calendar_agent
from src.agents.email_agent import email_agent
from src.agents.note_agent import note_agent
from src.agents.analytics_agent import analytics_agent


class AgentOrchestrator:
    """Orchestrates multi-agent workflows with parallel and sequential execution."""
    
    def __init__(self):
        self.agents = {
            "task": task_manager_agent,
            "calendar": calendar_agent,
            "email": email_agent,
            "note": note_agent,
            "analytics": analytics_agent
        }
    
    async def execute_sequential(self, user_id: str, 
                                 workflow: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute agents sequentially.
        
        Example workflow:
        [
            {"agent": "task", "action": "list"},
            {"agent": "analytics", "action": "daily_summary"}
        ]
        """
        logger.info(f"Starting sequential workflow with {len(workflow)} steps")
        
        results = []
        for step in workflow:
            agent_name = step.get("agent")
            agent = self.agents.get(agent_name)
            
            if not agent:
                logger.warning(f"Agent not found: {agent_name}")
                continue
            
            try:
                result = await agent.execute(user_id, step)
                results.append({
                    "step": step,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in sequential step: {e}")
                results.append({
                    "step": step,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return results
    
    async def execute_parallel(self, user_id: str, 
                              tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple agents in parallel.
        
        Example tasks:
        [
            {"agent": "task", "action": "list"},
            {"agent": "calendar", "action": "list"},
            {"agent": "email", "action": "prioritize"}
        ]
        """
        logger.info(f"Starting parallel execution with {len(tasks)} tasks")
        
        # Create coroutines for all tasks
        coroutines = []
        for task in tasks:
            agent_name = task.get("agent")
            agent = self.agents.get(agent_name)
            
            if agent:
                coroutines.append(agent.execute(user_id, task))
            else:
                logger.warning(f"Agent not found: {agent_name}")
        
        # Execute all in parallel
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                formatted_results.append({
                    "task": tasks[i],
                    "error": str(result),
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                formatted_results.append({
                    "task": tasks[i],
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return formatted_results
    
    async def execute_conditional(self, user_id: str, 
                                  workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute workflow with conditions.
        
        Example workflow:
        {
            "initial": {"agent": "task", "action": "list"},
            "conditions": [
                {
                    "if": "result['data']['total'] > 10",
                    "then": {"agent": "analytics", "action": "recommendations"}
                }
            ]
        }
        """
        logger.info("Starting conditional workflow")
        
        # Execute initial step
        initial = workflow.get("initial", {})
        agent = self.agents.get(initial.get("agent"))
        
        if not agent:
            return {"error": "Initial agent not found"}
        
        result = await agent.execute(user_id, initial)
        
        # Check conditions
        conditions = workflow.get("conditions", [])
        conditional_results = []
        
        for condition in conditions:
            condition_expr = condition.get("if", "")
            
            # Simple condition evaluation (in production, use safer evaluation)
            try:
                if eval(condition_expr, {"result": result}):
                    then_step = condition.get("then", {})
                    then_agent = self.agents.get(then_step.get("agent"))
                    
                    if then_agent:
                        cond_result = await then_agent.execute(user_id, then_step)
                        conditional_results.append({
                            "condition": condition_expr,
                            "matched": True,
                            "result": cond_result
                        })
            except Exception as e:
                logger.error(f"Error evaluating condition: {e}")
        
        return {
            "initial_result": result,
            "conditional_results": conditional_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def execute_morning_routine(self, user_id: str) -> Dict[str, Any]:
        """Execute a predefined morning routine workflow."""
        logger.info(f"Executing morning routine for user {user_id}")
        
        # Parallel: Get today's data
        morning_data = await self.execute_parallel(user_id, [
            {"agent": "task", "action": "list"},
            {"agent": "calendar", "action": "list", "days": 1},
            {"agent": "email", "action": "prioritize"}
        ])
        
        # Sequential: Generate summary and recommendations
        summary = await self.execute_sequential(user_id, [
            {"agent": "analytics", "action": "daily_summary"},
            {"agent": "analytics", "action": "recommendations"}
        ])
        
        return {
            "morning_data": morning_data,
            "summary": summary,
            "message": "Morning routine complete"
        }
    
    async def execute_weekly_review(self, user_id: str) -> Dict[str, Any]:
        """Execute weekly review workflow."""
        logger.info(f"Executing weekly review for user {user_id}")
        
        # Sequential workflow for comprehensive review
        review_steps = [
            {"agent": "analytics", "action": "weekly_report"},
            {"agent": "analytics", "action": "productivity_score"},
            {"agent": "analytics", "action": "trends"},
            {"agent": "analytics", "action": "recommendations"}
        ]
        
        results = await self.execute_sequential(user_id, review_steps)
        
        return {
            "review_results": results,
            "message": "Weekly review complete"
        }
    
    async def execute_smart_scheduling(self, user_id: str, 
                                      task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Smart task scheduling using multiple agents."""
        logger.info("Executing smart scheduling workflow")
        
        # Step 1: Analyze the task
        task_analysis = await task_manager_agent.execute(user_id, {
            "action": "create",
            **task_data
        })
        
        # Step 2: Find available time slots
        calendar_slots = await calendar_agent.execute(user_id, {
            "action": "find_slot",
            "duration": task_data.get("estimated_duration", 60)
        })
        
        # Step 3: Get AI recommendation on best time
        # (Would use additional AI logic here)
        
        return {
            "task": task_analysis,
            "available_slots": calendar_slots,
            "message": "Smart scheduling complete"
        }


# Global instance
agent_orchestrator = AgentOrchestrator()