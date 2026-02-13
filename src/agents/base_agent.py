"""Base agent class with memory and tool management."""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AgentMemory:
    """Agent persistent memory system using markdown and JSON."""

    def __init__(self, memory_dir: str):
        """Initialize agent memory system.

        Args:
            memory_dir: Directory path for storing memory files.
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.memory_dir / "session.json"
        self.context_file = self.memory_dir / "context.md"
        self.results_dir = self.memory_dir / "results"
        self.results_dir.mkdir(exist_ok=True)

    def save_session(self, session_data: Dict[str, Any]) -> None:
        """Persist session data to JSON file.

        Args:
            session_data: Dictionary containing session information.
        """
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, default=str)

    def load_session(self) -> Dict[str, Any]:
        """Load session data from JSON file.

        Returns:
            Dictionary containing session data or empty dict if not found.
        """
        if self.session_file.exists():
            with open(self.session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def append_context(self, context_entry: str) -> None:
        """Append to context markdown file.

        Args:
            context_entry: Markdown-formatted context entry.
        """
        timestamp = datetime.now().isoformat()
        with open(self.context_file, "a", encoding="utf-8") as f:
            f.write(f"\n## {timestamp}\n{context_entry}\n\n")

    def get_context(self) -> str:
        """Retrieve full context from markdown file.

        Returns:
            String containing all context entries.
        """
        if self.context_file.exists():
            with open(self.context_file, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def save_result(self, task_id: str, result: Dict[str, Any]) -> None:
        """Save task result to results directory.

        Args:
            task_id: Unique task identifier.
            result: Result data to save.
        """
        result_file = self.results_dir / f"result_{task_id}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(
        self,
        agent_id: str,
        role: str,
        memory_dir: str,
        api_key: str,
        model: str,
        system_prompt: str,
    ):
        """Initialize base agent.

        Args:
            agent_id: Unique identifier for the agent.
            role: Role name of the agent.
            memory_dir: Directory for agent memory storage.
            api_key: API key for LLM provider.
            model: Model identifier to use.
            system_prompt: System prompt for the agent.
        """
        self.agent_id = agent_id
        self.role = role
        self.memory = AgentMemory(memory_dir)
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt
        self.session = self.memory.load_session()
        self.logger = logging.getLogger(f"{self.__class__.__name__}:{agent_id}")

        # Initialize session if empty
        if not self.session:
            self.session = {
                "agent_id": agent_id,
                "role": role,
                "created_at": datetime.now().isoformat(),
                "tasks_completed": 0,
            }
            self.memory.save_session(self.session)

    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute assigned task. Must be implemented by subclasses.

        Args:
            task: Task dictionary containing task details.

        Returns:
            Dictionary containing task execution results.
        """
        pass

    def update_session(self, task_id: str, status: str) -> None:
        """Update agent session with task information.

        Args:
            task_id: Task identifier.
            status: Task status (completed, failed, etc.).
        """
        self.session["last_task_id"] = task_id
        self.session["last_task_status"] = status
        self.session["last_updated"] = datetime.now().isoformat()
        if status == "completed":
            self.session["tasks_completed"] = self.session.get("tasks_completed", 0) + 1
        self.memory.save_session(self.session)

    def save_task_result(self, task_id: str, result: Dict[str, Any]) -> None:
        """Save task result to memory.

        Args:
            task_id: Task identifier.
            result: Result data to save.
        """
        self.memory.save_result(task_id, result)
        self.memory.append_context(
            f"Completed task {task_id}: {result.get('status', 'unknown')}"
        )

    def get_tool_context(self) -> str:
        """Return available tools and their descriptions.

        Returns:
            String describing available tools.
        """
        return self.memory.get_context()

    async def call_llm(
        self, prompt: str, max_tokens: Optional[int] = None
    ) -> str:
        """Call LLM with given prompt using Groq.

        Args:
            prompt: User prompt to send to LLM.
            max_tokens: Maximum tokens in response.

        Returns:
            LLM response text.
        """
        try:
            from groq import Groq

            client = Groq(api_key=self.api_key)
            
            # Combine system prompt and user prompt
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens or 4096,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"LLM call failed: {str(e)}")
            raise

