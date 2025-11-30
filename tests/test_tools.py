"""Tests for tools and utilities."""
import pytest
from src.tools.email_api_tool import email_tool
from src.utils.helpers import generate_id, get_timestamp, safe_json_loads, safe_json_dumps


def test_email_tool_send():
    """Test email tool send functionality."""
    result = email_tool.send_email("test@example.com", "Test", "Test body")
    assert result is True


def test_email_tool_get():
    """Test email tool retrieval."""
    emails = email_tool.get_emails("test_user")
    assert isinstance(emails, list)


def test_generate_id():
    """Test ID generation."""
    id1 = generate_id()
    id2 = generate_id()
    assert id1 != id2
    assert len(id1) > 0


def test_get_timestamp():
    """Test timestamp generation."""
    ts = get_timestamp()
    assert "T" in ts  # ISO format check


def test_safe_json_loads():
    """Test safe JSON loading."""
    valid = safe_json_loads('{"key": "value"}')
    assert valid["key"] == "value"
    
    invalid = safe_json_loads("not json")
    assert invalid == {}


def test_safe_json_dumps():
    """Test safe JSON dumping."""
    result = safe_json_dumps({"test": "data"})
    assert "test" in result