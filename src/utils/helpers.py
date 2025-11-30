"""Utility helpers used across the project."""
import uuid
import json
from datetime import datetime
from typing import Any, Optional


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat()


def safe_json_loads(s: str, default: Optional[dict] = None) -> Any:
    """Safely parse JSON, return default if invalid."""
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return default or {}


def safe_json_dumps(obj: Any, default_str: str = "{}") -> str:
    """Safely serialize to JSON, return default string if invalid."""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return default_str