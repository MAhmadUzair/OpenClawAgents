"""Integration tests for workflow orchestration."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, AsyncMock

from src.workflow.workflow_engine import WorkflowEngine
from src.orchestration.task_manager import Coordinator, TaskQueue, TaskPriority


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace."""
    return str(tmp_path)


@pytest.fixture
def mock_api_key():
    """Mock API key."""
    return "test_api_key_12345"


@pytest.mark.asyncio
async def test_workflow_engine_initialization(mock_api_key, temp_workspace):
    """Test workflow engine initialization."""
    with patch("src.config.settings.EnvironmentConfig.WORKSPACE_DIR", temp_workspace):
        with patch("src.config.settings.EnvironmentConfig.TASK_QUEUE_DIR", temp_workspace):
            with patch("src.agents.base_agent.BaseAgent.call_llm"):
                engine = WorkflowEngine(mock_api_key)
                assert engine is not None
                assert len(engine.agents) > 0
                assert engine.coordinator is not None


@pytest.mark.asyncio
async def test_content_pipeline_creation(mock_api_key, temp_workspace):
    """Test content pipeline creation."""
    with patch("src.config.settings.EnvironmentConfig.WORKSPACE_DIR", temp_workspace):
        with patch("src.config.settings.EnvironmentConfig.TASK_QUEUE_DIR", temp_workspace):
            with patch("src.agents.base_agent.BaseAgent.call_llm") as mock_llm:
                mock_llm.return_value = "Test response"

                engine = WorkflowEngine(mock_api_key)
                topic = "Test Topic"

                pipeline = await engine.coordinator.execute_content_pipeline(topic)

                assert "pipeline_id" in pipeline
                assert "topic" in pipeline
                assert pipeline["topic"] == topic
                assert "tasks" in pipeline
                assert len(pipeline["tasks"]) == 5  # research, analysis, writing, seo, quality


@pytest.mark.asyncio
async def test_task_processing(mock_api_key, temp_workspace):
    """Test task processing."""
    with patch("src.config.settings.EnvironmentConfig.WORKSPACE_DIR", temp_workspace):
        with patch("src.config.settings.EnvironmentConfig.TASK_QUEUE_DIR", temp_workspace):
            with patch("src.agents.base_agent.BaseAgent.call_llm") as mock_llm:
                mock_llm.return_value = "Test response"

                engine = WorkflowEngine(mock_api_key)

                # Create a simple task
                task_id = engine.task_queue.add_task(
                    title="Test Task",
                    assigned_agent="agent:researcher:main",
                    payload={"topic": "Test", "max_sources": 2, "id": ""},
                )

                # Process tasks
                results = await engine.process_pending_tasks()

                assert "tasks_processed" in results
                assert "results" in results


def test_coordinator_initialization(mock_api_key, temp_workspace):
    """Test coordinator initialization."""
    with patch("src.config.settings.EnvironmentConfig.TASK_QUEUE_DIR", temp_workspace):
        task_queue = TaskQueue(temp_workspace)
        agents = {}
        coordinator = Coordinator(task_queue, agents)

        assert coordinator.task_queue == task_queue
        assert coordinator.agents == agents


@pytest.mark.asyncio
async def test_pipeline_task_dependencies(mock_api_key, temp_workspace):
    """Test that pipeline tasks have correct dependencies."""
    with patch("src.config.settings.EnvironmentConfig.WORKSPACE_DIR", temp_workspace):
        with patch("src.config.settings.EnvironmentConfig.TASK_QUEUE_DIR", temp_workspace):
            with patch("src.agents.base_agent.BaseAgent.call_llm"):
                engine = WorkflowEngine(mock_api_key)
                topic = "Test Topic"

                pipeline = await engine.coordinator.execute_content_pipeline(topic)

                # Check dependencies
                research_id = pipeline["tasks"]["research"]
                analysis_id = pipeline["tasks"]["analysis"]
                writing_id = pipeline["tasks"]["writing"]

                analysis_task = engine.task_queue.get_task(analysis_id)
                assert research_id in analysis_task.dependencies

                writing_task = engine.task_queue.get_task(writing_id)
                assert analysis_id in writing_task.dependencies


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

