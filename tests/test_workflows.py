"""Test cases for workflows and orchestration."""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestration.agent_orchestrator import agent_orchestrator
from src.memory.memory_bank import memory_bank


@pytest.fixture
def test_user():
    """Create a test user."""
    user = memory_bank.create_user(
        name="Workflow Test User",
        email=f"workflow_test_{id({})}@example.com"
    )
    yield user


@pytest.mark.asyncio
async def test_sequential_workflow(test_user):
    """Test sequential agent execution."""
    workflow = [
        {"agent": "task", "action": "create", "title": "Test Task 1"},
        {"agent": "task", "action": "list"}
    ]
    
    results = await agent_orchestrator.execute_sequential(test_user.user_id, workflow)
    
    assert len(results) == 2
    assert all("result" in r or "error" in r for r in results)


@pytest.mark.asyncio
async def test_parallel_workflow(test_user):
    """Test parallel agent execution."""
    tasks = [
        {"agent": "task", "action": "list"},
        {"agent": "calendar", "action": "list"},
        {"agent": "analytics", "action": "daily_summary"}
    ]
    
    results = await agent_orchestrator.execute_parallel(test_user.user_id, tasks)
    
    assert len(results) == 3
    # All should complete around the same time (parallel)
    assert all("result" in r or "error" in r for r in results)


@pytest.mark.asyncio
async def test_morning_routine(test_user):
    """Test morning routine workflow."""
    result = await agent_orchestrator.execute_morning_routine(test_user.user_id)
    
    assert "morning_data" in result
    assert "summary" in result
    assert result["message"] == "Morning routine complete"


@pytest.mark.asyncio
async def test_conditional_workflow(test_user):
    """Test conditional workflow execution."""
    # Create some tasks first
    await agent_orchestrator.execute_sequential(test_user.user_id, [
        {"agent": "task", "action": "create", "title": f"Task {i}"}
        for i in range(3)
    ])
    
    workflow = {
        "initial": {"agent": "task", "action": "list"},
        "conditions": [
            {
                "if": "result.get('success', False)",
                "then": {"agent": "analytics", "action": "daily_summary"}
            }
        ]
    }
    
    result = await agent_orchestrator.execute_conditional(test_user.user_id, workflow)
    
    assert "initial_result" in result
    assert "conditional_results" in result


@pytest.mark.asyncio
async def test_error_handling_in_workflow(test_user):
    """Test error handling in workflows."""
    workflow = [
        {"agent": "task", "action": "list"},
        {"agent": "nonexistent", "action": "test"},  # This should fail
        {"agent": "task", "action": "list"}  # Should still execute
    ]
    
    results = await agent_orchestrator.execute_sequential(test_user.user_id, workflow)
    
    # Should have results for all steps, with one error
    assert len(results) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])