"""Test cases for agents."""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.task_manager_agent import task_manager_agent
from src.memory.memory_bank import memory_bank
from src.models.schemas import TaskPriority


@pytest.fixture
def test_user():
    """Create a test user."""
    user = memory_bank.create_user(
        name="Test User",
        email=f"test_{id({})}@example.com"
    )
    yield user
    # Cleanup would go here


@pytest.mark.asyncio
async def test_create_task(test_user):
    """Test task creation."""
    result = await task_manager_agent.execute(
        user_id=test_user.user_id,
        input_data={
            "action": "create",
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "high"
        }
    )
    
    assert result["success"] is True
    assert "task_id" in result["data"]
    assert result["data"]["title"] == "Test Task"


@pytest.mark.asyncio
async def test_list_tasks(test_user):
    """Test listing tasks."""
    # Create a task first
    await task_manager_agent.execute(
        user_id=test_user.user_id,
        input_data={
            "action": "create",
            "title": "Task 1",
            "priority": "high"
        }
    )
    
    # List tasks
    result = await task_manager_agent.execute(
        user_id=test_user.user_id,
        input_data={"action": "list"}
    )
    
    assert result["success"] is True
    assert result["data"]["total"] >= 1


@pytest.mark.asyncio
async def test_complete_task(test_user):
    """Test completing a task."""
    # Create a task
    create_result = await task_manager_agent.execute(
        user_id=test_user.user_id,
        input_data={
            "action": "create",
            "title": "Task to Complete",
            "priority": "medium"
        }
    )
    
    task_id = create_result["data"]["task_id"]
    
    # Complete the task
    result = await task_manager_agent.execute(
        user_id=test_user.user_id,
        input_data={
            "action": "complete",
            "task_id": task_id
        }
    )
    
    assert result["success"] is True
    assert "Completed" in result["data"]["message"]


def test_memory_bank_operations(test_user):
    """Test memory bank operations."""
    # Create task
    task = memory_bank.create_task(
        user_id=test_user.user_id,
        title="Memory Test Task",
        priority=TaskPriority.HIGH
    )
    
    assert task.task_id is not None
    assert task.title == "Memory Test Task"
    
    # Retrieve tasks
    tasks = memory_bank.get_tasks(test_user.user_id)
    assert len(tasks) > 0


@pytest.mark.asyncio
async def test_agent_error_handling():
    """Test agent error handling."""
    result = await task_manager_agent.execute(
        user_id="non_existent_user",
        input_data={
            "action": "invalid_action",
            "data": {}
        }
    )
    
    assert result["success"] is False
    assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])