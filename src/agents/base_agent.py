"""Base agent class with common functionality."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from config.settings import settings
from config.logging_config import logger
from src.memory.session_manager import session_manager
from src.memory.memory_bank import memory_bank
import time


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.model = self._initialize_model()
        logger.info(f"Initialized agent: {name}")
    
    def _initialize_model(self):
        """Initialize the LLM model."""
        try:
            # import inside function to avoid import-time errors when package is not installed
            try:
                import google.generativeai as genai
            except Exception:
                logger.warning("google.generativeai not available; LLM calls will be mocked.")
                return None

            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(
                model_name=settings.model_name,
            )
            return self.model
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            return None
    
    @abstractmethod
    async def process(self, user_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process agent request. Must be implemented by subclasses."""
        pass
    
    async def execute(self, user_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent with logging and error handling."""
        start_time = time.time()
        
        try:
            logger.info(f"{self.name} started for user {user_id}")
            
            result = await self.process(user_id, input_data)
            
            execution_time = (time.time() - start_time) * 1000
            logger.info(f"{self.name} completed in {execution_time:.2f}ms")
            
            # Log to database
            self._log_execution(user_id, input_data, result, "success", execution_time)
            
            return {
                "success": True,
                "agent": self.name,
                "data": result,
                "execution_time_ms": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"{self.name} failed: {str(e)}")
            
            # Log error
            self._log_execution(user_id, input_data, None, "error", execution_time, str(e))
            
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "execution_time_ms": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _log_execution(self, user_id: str, input_data: Dict, output_data: Optional[Dict],
                      status: str, execution_time: float, error_msg: Optional[str] = None):
        """Log agent execution to database."""
        try:
            from src.models.database import AgentLogDB
            from sqlalchemy.orm import Session
            
            db: Session = memory_bank.get_db()
            
            log = AgentLogDB(
                user_id=user_id,
                agent_name=self.name,
                action="execute",
                input_data=input_data,
                output_data=output_data,
                status=status,
                execution_time_ms=execution_time,
                error_message=error_msg
            )
            
            db.add(log)
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Error logging execution: {e}")
    
    async def call_llm(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        """Call the LLM with a prompt."""
        try:
            if not self.model:
                # LLM not available; return a safe placeholder
                logger.debug("LLM not configured — returning placeholder response.")
                return "[LLM unavailable in this environment]"

            if context:
                # Build conversation history
                chat = self.model.start_chat(history=context)
                response = chat.send_message(prompt)
            else:
                response = self.model.generate_content(prompt)

            return response.text
            
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            raise
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context from session and memory."""
        # Get session context
        session_context = session_manager.get_context(user_id)
        
        # Get user profile
        user = memory_bank.get_user(user_id)
        
        return {
            "conversation_history": session_context,
            "user_profile": {
                "name": user.name if user else "User",
                "timezone": user.timezone if user else "UTC",
                "preferences": user.preferences if user else {}
            }
        }
    
    def build_system_prompt(self) -> str:
        """Build system prompt for the agent."""
        return f"""You are {self.name}, an AI agent that helps with productivity.
{self.description}

Your responsibilities:
- Be helpful, accurate, and concise
- Use tools when necessary
- Maintain context across conversations
- Respect user preferences and timezone

Always respond in a professional yet friendly manner."""
    
    async def send_message_to_agent(self, target_agent: str, message: Dict[str, Any]):
        """Send message to another agent (A2A communication)."""
        from src.models.schemas import AgentMessage
        import uuid
        
        msg = AgentMessage(
            msg_id=str(uuid.uuid4()),
            from_agent=self.name,
            to_agent=target_agent,
            message_type=message.get("type", "request"),
            payload=message.get("payload", {}),
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"A2A message: {self.name} -> {target_agent}")
        
        # In a real system, this would use a message queue
        # For now, we'll just log it
        return msg.dict()