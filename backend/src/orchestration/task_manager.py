"""Task management and inter-agent coordination."""

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task lifecycle states."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = 3
    MEDIUM = 2
    HIGH = 1
    CRITICAL = 0


@dataclass
class Task:
    """Task definition with dependencies."""

    id: str
    title: str
    assigned_agent: str
    status: TaskStatus
    priority: TaskPriority
    dependencies: List[str]
    payload: Dict[str, Any]
    created_at: str
    updated_at: str
    assigned_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        data = asdict(self)
        data["status"] = self.status.value
        data["priority"] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create task from dictionary."""
        data["status"] = TaskStatus(data["status"])
        data["priority"] = TaskPriority(data["priority"])
        return cls(**data)


class TaskQueue:
    """Persistent task queue with dependency management."""

    def __init__(self, queue_dir: str):
        """Initialize task queue.

        Args:
            queue_dir: Directory for storing task queue data.
        """
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_file = self.queue_dir / "tasks.json"
        self.completed_dir = self.queue_dir / "completed"
        self.completed_dir.mkdir(exist_ok=True)

    def add_task(
        self,
        title: str,
        assigned_agent: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None,
    ) -> str:
        """Create and queue a new task.

        Args:
            title: Task title.
            assigned_agent: Agent ID to assign task to.
            payload: Task payload data.
            priority: Task priority level.
            dependencies: List of task IDs this task depends on.

        Returns:
            Created task ID.
        """
        task_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()

        task = Task(
            id=task_id,
            title=title,
            assigned_agent=assigned_agent,
            status=TaskStatus.PENDING,
            priority=priority,
            dependencies=dependencies or [],
            payload=payload,
            created_at=now,
            updated_at=now,
        )

        self._persist_task(task)
        logger.info(f"Created task {task_id}: {title}")
        return task_id

    def get_pending_tasks(self, agent_id: str) -> List[Task]:
        """Get tasks ready for agent execution.

        Args:
            agent_id: Agent ID to get tasks for.

        Returns:
            List of pending tasks sorted by priority.
        """
        tasks = self._load_all_tasks()
        agent_tasks = [
            t
            for t in tasks
            if t.assigned_agent == agent_id
            and t.status == TaskStatus.PENDING
            and self._dependencies_satisfied(t, tasks)
        ]
        # Sort by priority (lower value = higher priority)
        return sorted(agent_tasks, key=lambda t: t.priority.value)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID.

        Args:
            task_id: Task ID to retrieve.

        Returns:
            Task object or None if not found.
        """
        tasks = self._load_all_tasks()
        return next((t for t in tasks if t.id == task_id), None)

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update task status with optional result.

        Args:
            task_id: Task ID to update.
            status: New task status.
            result: Optional task result data.
        """
        tasks = self._load_all_tasks()
        for task in tasks:
            if task.id == task_id:
                task.status = status
                task.updated_at = datetime.now().isoformat()
                if status == TaskStatus.IN_PROGRESS:
                    task.assigned_at = task.updated_at
                elif status == TaskStatus.COMPLETED:
                    task.completed_at = task.updated_at
                    task.result = result
                    # Move to completed directory
                    self._archive_task(task)
                break
        self._persist_tasks(tasks)
        logger.info(f"Updated task {task_id} to status: {status.value}")

    def _dependencies_satisfied(self, task: Task, all_tasks: List[Task]) -> bool:
        """Check if all task dependencies are completed.

        Args:
            task: Task to check dependencies for.
            all_tasks: All tasks in the system.

        Returns:
            True if all dependencies are satisfied, False otherwise.
        """
        if not task.dependencies:
            return True

        for dep_id in task.dependencies:
            dep_task = next((t for t in all_tasks if t.id == dep_id), None)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    def _persist_task(self, task: Task) -> None:
        """Save task to persistent storage.

        Args:
            task: Task to persist.
        """
        tasks = self._load_all_tasks()
        tasks.append(task)
        self._persist_tasks(tasks)

    def _load_all_tasks(self) -> List[Task]:
        """Load all tasks from storage.

        Returns:
            List of all tasks.
        """
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [Task.from_dict(t) for t in data]
            except Exception as e:
                logger.error(f"Failed to load tasks: {e}")
                return []
        return []

    def _persist_tasks(self, tasks: List[Task]) -> None:
        """Write tasks to storage.

        Args:
            tasks: List of tasks to persist.
        """
        try:
            with open(self.tasks_file, "w", encoding="utf-8") as f:
                json.dump([t.to_dict() for t in tasks], f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to persist tasks: {e}")

    def _archive_task(self, task: Task) -> None:
        """Archive completed task.

        Args:
            task: Task to archive.
        """
        try:
            archive_file = self.completed_dir / f"task_{task.id}.json"
            with open(archive_file, "w", encoding="utf-8") as f:
                json.dump(task.to_dict(), f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to archive task {task.id}: {e}")

    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get result from completed task.

        Args:
            task_id: Task ID to get result for.

        Returns:
            Task result dictionary or None if not found.
        """
        task = self.get_task(task_id)
        if task and task.result:
            return task.result

        # Check archived tasks
        archive_file = self.completed_dir / f"task_{task_id}.json"
        if archive_file.exists():
            try:
                with open(archive_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("result")
            except Exception as e:
                logger.warning(f"Failed to load archived task result: {e}")

        return None


class Coordinator:
    """Central coordination engine for workflow orchestration."""

    def __init__(self, task_queue: TaskQueue, agents: Dict[str, Any]):
        """Initialize coordinator.

        Args:
            task_queue: Task queue instance.
            agents: Dictionary of available agents.
        """
        self.task_queue = task_queue
        self.agents = agents

    async def execute_content_pipeline(self, topic: str) -> Dict[str, Any]:
        """Execute complete content research and publishing pipeline.

        Args:
            topic: Research topic for the pipeline.

        Returns:
            Dictionary with pipeline information and task IDs.
        """
        pipeline_id = str(uuid.uuid4())[:8]

        # Step 1: Research task
        research_task_id = self.task_queue.add_task(
            title=f"Research: {topic}",
            assigned_agent="agent:researcher:main",
            payload={"topic": topic, "max_sources": 5, "id": ""},
            priority=TaskPriority.HIGH,
        )

        # Step 2: Analysis task (depends on research)
        analysis_task_id = self.task_queue.add_task(
            title=f"Analyze: {topic}",
            assigned_agent="agent:analyst:main",
            payload={
                "research_task_id": research_task_id,
                "research_data": {},
                "id": "",
            },
            dependencies=[research_task_id],
            priority=TaskPriority.HIGH,
        )

        # Step 3: Writing task (depends on analysis)
        writing_task_id = self.task_queue.add_task(
            title=f"Write: {topic}",
            assigned_agent="agent:writer:main",
            payload={
                "analysis_task_id": analysis_task_id,
                "outline": {},
                "style_guide": "professional",
                "research_data": {},
                "id": "",
            },
            dependencies=[analysis_task_id],
            priority=TaskPriority.MEDIUM,
        )

        # Step 4: SEO optimization (depends on writing)
        seo_task_id = self.task_queue.add_task(
            title=f"SEO Optimize: {topic}",
            assigned_agent="agent:seo:main",
            payload={
                "writing_task_id": writing_task_id,
                "content": "",
                "topic": topic,
                "id": "",
            },
            dependencies=[writing_task_id],
            priority=TaskPriority.MEDIUM,
        )

        # Step 5: Quality check (depends on SEO)
        quality_task_id = self.task_queue.add_task(
            title=f"Quality Check: {topic}",
            assigned_agent="agent:quality:main",
            payload={
                "seo_task_id": seo_task_id,
                "content": "",
                "seo_data": {},
                "id": "",
            },
            dependencies=[seo_task_id],
            priority=TaskPriority.HIGH,
        )

        return {
            "pipeline_id": pipeline_id,
            "topic": topic,
            "tasks": {
                "research": research_task_id,
                "analysis": analysis_task_id,
                "writing": writing_task_id,
                "seo": seo_task_id,
                "quality": quality_task_id,
            },
        }

