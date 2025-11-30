"""Session management for short-term memory."""
import json
import redis
from typing import Optional, Dict, Any
from datetime import timedelta
from config.settings import settings
from config.logging_config import logger


class SessionManager:
    """Manages short-term session state using Redis."""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
        self.ttl = settings.session_ttl
    
    def _get_key(self, user_id: str, key: str) -> str:
        """Generate Redis key."""
        return f"session:{user_id}:{key}"
    
    def set(self, user_id: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store session data."""
        try:
            redis_key = self._get_key(user_id, key)
            serialized = json.dumps(value)
            expire_time = ttl or self.ttl
            
            self.redis_client.setex(
                redis_key,
                timedelta(seconds=expire_time),
                serialized
            )
            logger.debug(f"Session set: {redis_key}")
            return True
        except Exception as e:
            logger.error(f"Error setting session: {e}")
            return False
    
    def get(self, user_id: str, key: str) -> Optional[Any]:
        """Retrieve session data."""
        try:
            redis_key = self._get_key(user_id, key)
            data = self.redis_client.get(redis_key)
            
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    def delete(self, user_id: str, key: str) -> bool:
        """Delete session data."""
        try:
            redis_key = self._get_key(user_id, key)
            self.redis_client.delete(redis_key)
            logger.debug(f"Session deleted: {redis_key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    def get_all(self, user_id: str) -> Dict[str, Any]:
        """Get all session data for a user."""
        try:
            pattern = f"session:{user_id}:*"
            keys = self.redis_client.keys(pattern)
            
            result = {}
            for key in keys:
                # Extract the actual key name
                key_name = key.split(":")[-1]
                data = self.redis_client.get(key)
                if data:
                    result[key_name] = json.loads(data)
            
            return result
        except Exception as e:
            logger.error(f"Error getting all sessions: {e}")
            return {}
    
    def clear_user_sessions(self, user_id: str) -> bool:
        """Clear all sessions for a user."""
        try:
            pattern = f"session:{user_id}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
            
            logger.info(f"Cleared {len(keys)} sessions for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing user sessions: {e}")
            return False
    
    def update_context(self, user_id: str, message: str, response: str):
        """Update conversation context."""
        try:
            context_key = "conversation_context"
            context = self.get(user_id, context_key) or []
            
            # Keep last 10 exchanges
            if len(context) >= 20:
                context = context[-18:]
            
            context.extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ])
            
            self.set(user_id, context_key, context)
        except Exception as e:
            logger.error(f"Error updating context: {e}")
    
    def get_context(self, user_id: str) -> list:
        """Get conversation context."""
        return self.get(user_id, "conversation_context") or []


# Global session manager instance
session_manager = SessionManager()