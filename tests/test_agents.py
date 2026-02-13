"""Comprehensive test suite for agent system."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.agents.base_agent import ResearchAgent, WriterAgent, AgentMemory
from src.orchestration.task_manager import (
    TaskQueue,
    TaskStatus,
    TaskPriority,
    Task,
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace for testing."""
    return str(tmp_path)


@pytest.fixture
def agent_memory(temp_workspace):
    """Create memory instance."""
    return AgentMemory(temp_workspace)


@pytest.fixture
def task_queue(temp_workspace):
    """Create task queue instance."""
    return TaskQueue(temp_workspace)


def test_agent_memory_persistence(agent_memory):
    """Test memory save and load."""
    session_data = {"user_id": "test_user", "status": "active"}
    agent_memory.save_session(session_data)
    loaded = agent_memory.load_session()
    assert loaded == session_data


def test_agent_memory_context(agent_memory):
    """Test context append and retrieval."""
    agent_memory.append_context("Test context entry")
    context = agent_memory.get_context()
    assert "Test context entry" in context


def test_task_queue_creation(task_queue):
    """Test task queue initialization."""
    task_id = task_queue.add_task(
        title="Test Task",
        assigned_agent="test_agent",
        payload={"test": "data"},
    )
    assert task_id is not None
    assert len(task_id) > 0


def test_task_queue_retrieval(task_queue):
    """Test task retrieval."""
    task_id = task_queue.add_task(
        title="Test Task",
        assigned_agent="test_agent",
        payload={"test": "data"},
    )
    task = task_queue.get_task(task_id)
    assert task is not None
    assert task.title == "Test Task"
    assert task.assigned_agent == "test_agent"


def test_task_dependencies(task_queue):
    """Test task dependency management."""
    # Create parent task
    parent_id = task_queue.add_task(
        title="Parent Task",
        assigned_agent="agent1",
        payload={},
    )

    # Create dependent task
    child_id = task_queue.add_task(
        title="Child Task",
        assigned_agent="agent2",
        payload={},
        dependencies=[parent_id],
    )

    # Child should not be available until parent completes
    pending = task_queue.get_pending_tasks("agent2")
    assert len(pending) == 0

    # Complete parent task
    task_queue.update_task_status(parent_id, TaskStatus.COMPLETED)

    # Now child should be available
    pending = task_queue.get_pending_tasks("agent2")
    assert len(pending) == 1
    assert pending[0].id == child_id


@pytest.mark.asyncio
async def test_research_agent_execution(temp_workspace):
    """Test research agent task execution."""
    with patch("src.agents.research_agent.ResearchAgent.call_llm") as mock_llm:
        mock_llm.return_value = "Test research response"

        agent = ResearchAgent(
            agent_id="test:researcher",
            role="Test Researcher",
            memory_dir=temp_workspace,
            api_key="test_key",
            model="test_model",
            system_prompt="Test prompt",
        )

        task = {
            "id": "task_001",
            "topic": "Test Topic",
            "max_sources": 3,
        }

        result = await agent.execute_task(task)

        assert result["status"] == "completed"
        assert result["agent"] == "test:researcher"
        assert "sources_found" in result
        assert result["sources_found"] > 0


@pytest.mark.asyncio
async def test_writer_agent_execution(temp_workspace):
    """Test writer agent task execution."""
    with patch("src.agents.writer_agent.WriterAgent.call_llm") as mock_llm:
        mock_llm.return_value = "# Test Article\n\nContent here."

        agent = WriterAgent(
            agent_id="test:writer",
            role="Test Writer",
            memory_dir=temp_workspace,
            api_key="test_key",
            model="test_model",
            system_prompt="Test prompt",
        )

        task = {
            "id": "task_002",
            "outline": {
                "title": "Test Article",
                "sections": [{"title": "Section 1", "subsections": []}],
            },
            "style_guide": "professional",
            "research_data": {},
        }

        result = await agent.execute_task(task)

        assert result["status"] == "completed"
        assert "content" in result
        assert "word_count" in result
        assert result["word_count"] > 0


def test_task_priority_ordering(task_queue):
    """Test tasks are ordered by priority."""
    # Add tasks with different priorities
    task_queue.add_task(
        "Low Priority", "agent1", {}, priority=TaskPriority.LOW
    )
    task_queue.add_task(
        "High Priority", "agent1", {}, priority=TaskPriority.HIGH
    )
    task_queue.add_task(
        "Critical", "agent1", {}, priority=TaskPriority.CRITICAL
    )

    pending = task_queue.get_pending_tasks("agent1")
    assert len(pending) == 3

    # Should be ordered by priority
    assert pending[0].priority == TaskPriority.CRITICAL
    assert pending[1].priority == TaskPriority.HIGH
    assert pending[2].priority == TaskPriority.LOW


def test_task_status_updates(task_queue):
    """Test task status updates."""
    task_id = task_queue.add_task(
        title="Test Task",
        assigned_agent="test_agent",
        payload={},
    )

    # Update to in progress
    task_queue.update_task_status(task_id, TaskStatus.IN_PROGRESS)
    task = task_queue.get_task(task_id)
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.assigned_at is not None

    # Update to completed
    result = {"status": "completed", "data": "test"}
    task_queue.update_task_status(task_id, TaskStatus.COMPLETED, result)
    task = task_queue.get_task(task_id)
    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at is not None
    assert task.result == result


def test_task_result_retrieval(task_queue):
    """Test retrieving task results."""
    task_id = task_queue.add_task(
        title="Test Task",
        assigned_agent="test_agent",
        payload={},
    )

    result = {"status": "completed", "data": "test"}
    task_queue.update_task_status(task_id, TaskStatus.COMPLETED, result)

    retrieved_result = task_queue.get_task_result(task_id)
    assert retrieved_result == result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

