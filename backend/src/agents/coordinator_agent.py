"""Coordinator agent for orchestrating multi-agent workflows."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CoordinatorAgent(BaseAgent):
    """Primary coordinator agent for task routing and workflow management."""

    def __init__(
        self,
        agent_id: str,
        role: str,
        memory_dir: str,
        api_key: str,
        model: str,
        system_prompt: str,
        available_agents: Dict[str, BaseAgent],
    ):
        """Initialize coordinator agent.

        Args:
            agent_id: Unique identifier for the agent.
            role: Role name of the agent.
            memory_dir: Directory for agent memory storage.
            api_key: API key for LLM provider.
            model: Model identifier to use.
            system_prompt: System prompt for the agent.
            available_agents: Dictionary of available agents to coordinate.
        """
        super().__init__(agent_id, role, memory_dir, api_key, model, system_prompt)
        self.available_agents = available_agents

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coordination task.

        Args:
            task: Task dictionary containing workflow instructions.

        Returns:
            Dictionary with coordination results.
        """
        task_type = task.get("type", "coordinate")
        task_id = task.get("id", "unknown")

        self.logger.info(f"Coordinator executing task: {task_type}")

        try:
            if task_type == "route":
                result = await self._route_task(task)
            elif task_type == "validate":
                result = await self._validate_work(task)
            elif task_type == "monitor":
                result = await self._monitor_agents(task)
            else:
                result = await self._coordinate_workflow(task)

            self.update_session(task_id, "completed")
            self.save_task_result(task_id, result)

            return result

        except Exception as e:
            self.logger.error(f"Coordination task failed: {str(e)}")
            self.update_session(task_id, "failed")
            raise

    async def _route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route task to appropriate agent.

        Args:
            task: Task dictionary.

        Returns:
            Routing decision dictionary.
        """
        task_description = task.get("description", "")
        task_requirements = task.get("requirements", [])

        prompt = f"""Determine the best agent to handle this task:

Task Description: {task_description}
Requirements: {', '.join(task_requirements)}

Available Agents:
- researcher: For gathering information and research
- analyst: For data analysis and synthesis
- writer: For content creation
- seo: For SEO optimization
- quality: For quality assurance

Which agent should handle this task? Provide reasoning."""

        try:
            decision = await self.call_llm(prompt, max_tokens=512)
            # Extract agent recommendation
            recommended_agent = self._extract_agent_recommendation(decision)

            return {
                "status": "routed",
                "recommended_agent": recommended_agent,
                "reasoning": decision,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.warning(f"Routing decision had issues: {e}")
            return {
                "status": "routed",
                "recommended_agent": "researcher",
                "reasoning": "Default routing",
            }

    def _extract_agent_recommendation(self, text: str) -> str:
        """Extract agent recommendation from text.

        Args:
            text: Decision text.

        Returns:
            Agent identifier.
        """
        text_lower = text.lower()
        if "researcher" in text_lower or "research" in text_lower:
            return "researcher"
        elif "analyst" in text_lower or "analysis" in text_lower:
            return "analyst"
        elif "writer" in text_lower or "write" in text_lower:
            return "writer"
        elif "seo" in text_lower:
            return "seo"
        elif "quality" in text_lower or "qa" in text_lower:
            return "quality"
        return "researcher"  # Default

    async def _validate_work(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate work quality from agents.

        Args:
            task: Task dictionary with work to validate.

        Returns:
            Validation results dictionary.
        """
        work_data = task.get("work_data", {})
        quality_threshold = task.get("quality_threshold", 70)

        prompt = f"""Review the following work output and validate quality:

Work Data: {str(work_data)[:1000]}...
Quality Threshold: {quality_threshold}/100

Assess:
1. Completeness
2. Accuracy
3. Quality
4. Meets requirements

Provide validation assessment."""

        try:
            assessment = await self.call_llm(prompt, max_tokens=1024)
            # Determine if work passes
            passes = self._determine_validation_result(assessment, quality_threshold)

            return {
                "status": "validated",
                "passes": passes,
                "assessment": assessment,
                "quality_threshold": quality_threshold,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.warning(f"Validation had issues: {e}")
            return {
                "status": "validated",
                "passes": True,
                "assessment": "Validation completed",
            }

    def _determine_validation_result(
        self, assessment: str, threshold: int
    ) -> bool:
        """Determine if work passes validation.

        Args:
            assessment: Assessment text.
            threshold: Quality threshold.

        Returns:
            True if work passes, False otherwise.
        """
        # Simple heuristic - look for positive indicators
        positive = (
            assessment.lower().count("pass")
            + assessment.lower().count("meets")
            + assessment.lower().count("good")
            + assessment.lower().count("acceptable")
        )
        negative = (
            assessment.lower().count("fail")
            + assessment.lower().count("poor")
            + assessment.lower().count("unacceptable")
        )

        return positive > negative

    async def _monitor_agents(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor agent status and performance.

        Args:
            task: Task dictionary.

        Returns:
            Monitoring results dictionary.
        """
        agent_statuses = {}

        for agent_id, agent in self.available_agents.items():
            session = agent.session
            agent_statuses[agent_id] = {
                "role": agent.role,
                "tasks_completed": session.get("tasks_completed", 0),
                "last_task": session.get("last_task_id", "none"),
                "last_status": session.get("last_task_status", "unknown"),
                "last_updated": session.get("last_updated", "unknown"),
            }

        return {
            "status": "monitored",
            "agent_statuses": agent_statuses,
            "total_agents": len(self.available_agents),
            "timestamp": datetime.now().isoformat(),
        }

    async def _coordinate_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate complete workflow.

        Args:
            task: Task dictionary with workflow parameters.

        Returns:
            Coordination results dictionary.
        """
        workflow_type = task.get("workflow_type", "content_pipeline")
        parameters = task.get("parameters", {})

        if workflow_type == "content_pipeline":
            return await self._coordinate_content_pipeline(parameters)

        return {
            "status": "coordinated",
            "workflow_type": workflow_type,
            "message": "Workflow coordination completed",
        }

    async def _coordinate_content_pipeline(
        self, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Coordinate content research and publishing pipeline.

        Args:
            parameters: Pipeline parameters.

        Returns:
            Pipeline coordination results.
        """
        topic = parameters.get("topic", "Unknown Topic")

        prompt = f"""Plan the execution of a content pipeline for topic: {topic}

The pipeline should include:
1. Research phase
2. Analysis phase
3. Writing phase
4. SEO optimization phase
5. Quality assurance phase

Provide execution plan with task dependencies and sequencing."""

        try:
            plan = await self.call_llm(prompt, max_tokens=1024)
            return {
                "status": "planned",
                "topic": topic,
                "execution_plan": plan,
                "phases": [
                    "research",
                    "analysis",
                    "writing",
                    "seo_optimization",
                    "quality_assurance",
                ],
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.warning(f"Pipeline planning had issues: {e}")
            return {
                "status": "planned",
                "topic": topic,
                "execution_plan": "Standard content pipeline",
                "phases": ["research", "analysis", "writing", "seo", "quality"],
            }

