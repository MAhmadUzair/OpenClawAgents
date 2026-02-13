"""Main workflow orchestration engine."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config.settings import (
    AGENT_CONFIGURATIONS,
    EnvironmentConfig,
)
from src.agents.base_agent import BaseAgent
from src.agents.research_agent import ResearchAgent
from src.agents.analyst_agent import AnalystAgent
from src.agents.writer_agent import WriterAgent
from src.agents.seo_agent import SEOAgent
from src.agents.quality_agent import QualityAgent
from src.agents.coordinator_agent import CoordinatorAgent
from src.orchestration.task_manager import (
    Coordinator,
    TaskQueue,
    TaskStatus,
    TaskPriority,
)

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Main workflow orchestration engine."""

    def __init__(self, api_key: str):
        """Initialize workflow engine.

        Args:
            api_key: API key for LLM provider.
        """
        self.api_key = api_key
        EnvironmentConfig.ensure_directories()

        self.task_queue = TaskQueue(EnvironmentConfig.TASK_QUEUE_DIR)
        self.agents: Dict[str, BaseAgent] = {}
        self.coordinator: Optional[Coordinator] = None

        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize all configured agents."""
        for agent_name, config in AGENT_CONFIGURATIONS.items():
            Path(config.workspace_path).mkdir(parents=True, exist_ok=True)

            agent = None

            if agent_name == "researcher":
                agent = ResearchAgent(
                    agent_id=config.agent_id,
                    role=config.role_name,
                    memory_dir=config.workspace_path,
                    api_key=self.api_key,
                    model=config.model_config.primary,
                    system_prompt=config.system_prompt,
                )
            elif agent_name == "analyst":
                agent = AnalystAgent(
                    agent_id=config.agent_id,
                    role=config.role_name,
                    memory_dir=config.workspace_path,
                    api_key=self.api_key,
                    model=config.model_config.primary,
                    system_prompt=config.system_prompt,
                )
            elif agent_name == "writer":
                agent = WriterAgent(
                    agent_id=config.agent_id,
                    role=config.role_name,
                    memory_dir=config.workspace_path,
                    api_key=self.api_key,
                    model=config.model_config.primary,
                    system_prompt=config.system_prompt,
                )
            elif agent_name == "seo_specialist":
                agent = SEOAgent(
                    agent_id=config.agent_id,
                    role=config.role_name,
                    memory_dir=config.workspace_path,
                    api_key=self.api_key,
                    model=config.model_config.primary,
                    system_prompt=config.system_prompt,
                )
            elif agent_name == "quality_checker":
                agent = QualityAgent(
                    agent_id=config.agent_id,
                    role=config.role_name,
                    memory_dir=config.workspace_path,
                    api_key=self.api_key,
                    model=config.model_config.primary,
                    system_prompt=config.system_prompt,
                )
            elif agent_name == "coordinator":
                # Coordinator will be initialized after other agents
                continue

            if agent:
                self.agents[config.agent_id] = agent
                logger.info(f"Initialized {config.role_name}: {config.agent_id}")

        # Initialize coordinator with available agents
        coordinator_config = AGENT_CONFIGURATIONS["coordinator"]
        coordinator_agent = CoordinatorAgent(
            agent_id=coordinator_config.agent_id,
            role=coordinator_config.role_name,
            memory_dir=coordinator_config.workspace_path,
            api_key=self.api_key,
            model=coordinator_config.model_config.primary,
            system_prompt=coordinator_config.system_prompt,
            available_agents=self.agents,
        )
        self.agents[coordinator_config.agent_id] = coordinator_agent

        # Initialize coordinator
        self.coordinator = Coordinator(self.task_queue, self.agents)
        logger.info("Workflow engine initialized")

    async def process_pending_tasks(self) -> Dict[str, Any]:
        """Process all pending tasks for each agent.

        Returns:
            Dictionary with processing results.
        """
        results = {}
        tasks_processed = 0

        for agent_id, agent in self.agents.items():
            if agent_id == "agent:coordinator:main":
                continue  # Skip coordinator for now

            pending_tasks = self.task_queue.get_pending_tasks(agent_id)

            for task in pending_tasks:
                logger.info(f"Processing task {task.id}: {task.title}")
                self.task_queue.update_task_status(task.id, TaskStatus.IN_PROGRESS)

                try:
                    # Update task payload with ID
                    task.payload["id"] = task.id
                    
                    # Load data from dependent tasks before execution
                    self._load_dependent_task_data(task)

                    # Execute task
                    result = await agent.execute_task(task.payload)

                    # Update task status
                    self.task_queue.update_task_status(
                        task.id, TaskStatus.COMPLETED, result
                    )

                    results[task.id] = result
                    tasks_processed += 1
                    logger.info(f"Task {task.id} completed successfully")

                except Exception as e:
                    logger.error(f"Task {task.id} failed: {str(e)}")
                    self.task_queue.update_task_status(task.id, TaskStatus.FAILED)
                    results[task.id] = {"status": "failed", "error": str(e)}

        return {"tasks_processed": tasks_processed, "results": results}

    def _load_dependent_task_data(self, task) -> None:
        """Load data from dependent tasks into current task payload.

        Args:
            task: Task to load data for.
        """
        # Load research data for analyst
        if "research_task_id" in task.payload:
            research_task_id = task.payload.get("research_task_id")
            if research_task_id:
                research_result = self.task_queue.get_task_result(research_task_id)
                if research_result:
                    task.payload["research_data"] = research_result
                    logger.info(f"Loaded research data for task {task.id}")

        # Load analysis data (outline + research) for writer
        if "analysis_task_id" in task.payload:
            analysis_task_id = task.payload.get("analysis_task_id")
            if analysis_task_id:
                analysis_result = self.task_queue.get_task_result(analysis_task_id)
                if analysis_result:
                    task.payload["outline"] = analysis_result.get("outline", {})
                    # Also load research data
                    research_task_id = task.payload.get("research_task_id")
                    if research_task_id:
                        research_result = self.task_queue.get_task_result(
                            research_task_id
                        )
                        if research_result:
                            task.payload["research_data"] = research_result
                    logger.info(f"Loaded analysis data for task {task.id}")

        # Load writing data for SEO
        if "writing_task_id" in task.payload:
            writing_task_id = task.payload.get("writing_task_id")
            if writing_task_id:
                writing_result = self.task_queue.get_task_result(writing_task_id)
                if writing_result:
                    task.payload["content"] = writing_result.get("content", "")
                    task.payload["topic"] = writing_result.get("topic", "")
                    logger.info(f"Loaded writing data for task {task.id}")

        # Load SEO data for quality
        if "seo_task_id" in task.payload:
            seo_task_id = task.payload.get("seo_task_id")
            if seo_task_id:
                seo_result = self.task_queue.get_task_result(seo_task_id)
                if seo_result:
                    task.payload["content"] = seo_result.get("optimized_content", "")
                    task.payload["seo_data"] = seo_result
                    logger.info(f"Loaded SEO data for task {task.id}")

    def _propagate_task_data(self, task_id: str, result: Dict[str, Any]) -> None:
        """Propagate task result data to dependent tasks (legacy method, kept for compatibility).

        Args:
            task_id: Completed task ID.
            result: Task result data.
        """
        # Data is now loaded on-demand in _load_dependent_task_data
        pass

    async def run_content_pipeline(self, topic: str) -> Dict[str, Any]:
        """Execute complete content research and publishing pipeline.

        Args:
            topic: Research topic for the pipeline.

        Returns:
            Dictionary with pipeline execution results.
        """
        logger.info(f"Starting content pipeline for: {topic}")

        # Create pipeline
        pipeline = await self.coordinator.execute_content_pipeline(topic)
        logger.info(f"Pipeline created: {json.dumps(pipeline, indent=2)}")

        # Process tasks iteratively until all complete
        max_iterations = EnvironmentConfig.MAX_ITERATIONS
        iteration = 0
        all_results = {}

        while iteration < max_iterations:
            # Propagate data from completed tasks
            completed_tasks = [
                t
                for t in self.task_queue._load_all_tasks()
                if t.status == TaskStatus.COMPLETED and t.result
            ]
            for task in completed_tasks:
                self._propagate_task_data(task.id, task.result)

            # Process pending tasks
            processing_results = await self.process_pending_tasks()

            if processing_results["tasks_processed"] == 0:
                # Check if all tasks are complete
                all_tasks = self.task_queue._load_all_tasks()
                pipeline_tasks = [
                    t
                    for t in all_tasks
                    if t.id in pipeline["tasks"].values()
                ]
                if all(t.status == TaskStatus.COMPLETED for t in pipeline_tasks):
                    logger.info("All pipeline tasks completed")
                    break
                elif all(
                    t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                    for t in pipeline_tasks
                ):
                    logger.warning("Pipeline completed with some failures")
                    break

            all_results.update(processing_results["results"])
            iteration += 1
            await asyncio.sleep(1)

        # Collect final results
        final_results = {}
        for task_id in pipeline["tasks"].values():
            task = self.task_queue.get_task(task_id)
            if task and task.result:
                final_results[task_id] = task.result

        logger.info(f"Pipeline execution completed after {iteration} iterations")

        return {
            "pipeline": pipeline,
            "iterations": iteration,
            "results": final_results,
        }

    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get status of a pipeline.

        Args:
            pipeline_id: Pipeline ID.

        Returns:
            Dictionary with pipeline status.
        """
        all_tasks = self.task_queue._load_all_tasks()
        status = {
            "pipeline_id": pipeline_id,
            "tasks": {},
            "overall_status": "unknown",
        }

        for task in all_tasks:
            status["tasks"][task.id] = {
                "title": task.title,
                "status": task.status.value,
                "agent": task.assigned_agent,
            }

        # Determine overall status
        task_statuses = [t["status"] for t in status["tasks"].values()]
        if all(s == "completed" for s in task_statuses):
            status["overall_status"] = "completed"
        elif any(s == "failed" for s in task_statuses):
            status["overall_status"] = "failed"
        elif any(s == "in_progress" for s in task_statuses):
            status["overall_status"] = "in_progress"
        else:
            status["overall_status"] = "pending"

        return status

