"""Production agent configuration following PEP8 standards."""

import os
from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    """Model configuration with fallbacks."""

    primary: str
    fallbacks: List[str]
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class AgentRole:
    """Individual agent configuration."""

    agent_id: str
    role_name: str
    model_config: ModelConfig
    system_prompt: str
    tools: List[str]
    workspace_path: str
    heartbeat_interval: int  # seconds


class EnvironmentConfig:
    """Runtime environment settings."""

    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Directories
    WORKSPACE_DIR: str = os.getenv("WORKSPACE_DIR", "./workspace")
    MEMORY_DIR: str = os.getenv("MEMORY_DIR", "./workspace/shared_memory")
    TASK_QUEUE_DIR: str = os.getenv("TASK_QUEUE_DIR", "./workspace/task_queue")

    # Execution
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 60
    MAX_ITERATIONS: int = 20

    @classmethod
    def ensure_directories(cls) -> None:
        """Create all required directories."""
        Path(cls.WORKSPACE_DIR).mkdir(parents=True, exist_ok=True)
        Path(cls.MEMORY_DIR).mkdir(parents=True, exist_ok=True)
        Path(cls.TASK_QUEUE_DIR).mkdir(parents=True, exist_ok=True)


# Agent Configurations
AGENT_CONFIGURATIONS: Dict[str, AgentRole] = {
    "coordinator": AgentRole(
        agent_id="agent:coordinator:main",
        role_name="Primary Coordinator",
        model_config=ModelConfig(
            primary="llama-3.3-70b-versatile",
            fallbacks=["llama-3.1-8b-instant"],
            max_tokens=8192,
            temperature=0.5,
        ),
        system_prompt="""You are the primary coordinator managing a content research and publishing pipeline.
Your responsibilities:
- Route research requests to appropriate agents
- Validate work quality before publishing
- Manage task dependencies and sequencing
- Monitor agent status and memory usage
- Make decisions about task routing and prioritization""",
        tools=["task_dispatcher", "memory_reader", "quality_checker"],
        workspace_path="./workspace/coordinator",
        heartbeat_interval=300,
    ),
    "researcher": AgentRole(
        agent_id="agent:researcher:main",
        role_name="Research Specialist",
        model_config=ModelConfig(
            primary="llama-3.1-8b-instant",
            fallbacks=["llama-3.3-70b-versatile"],
            max_tokens=4096,
            temperature=0.3,
        ),
        system_prompt="""You are a research specialist gathering information from multiple sources.
Your responsibilities:
- Search and collect relevant sources on given topics
- Summarize findings with proper citations
- Identify gaps in information
- Flag unreliable or contradictory sources
- Organize research findings in structured format""",
        tools=["web_search", "source_aggregator", "citation_formatter"],
        workspace_path="./workspace/researcher",
        heartbeat_interval=600,
    ),
    "analyst": AgentRole(
        agent_id="agent:analyst:main",
        role_name="Data Analyst",
        model_config=ModelConfig(
            primary="llama-3.3-70b-versatile",
            fallbacks=["llama-3.1-8b-instant"],
            max_tokens=4096,
            temperature=0.4,
        ),
        system_prompt="""You are a data analyst synthesizing research findings.
Your responsibilities:
- Cross-reference sources for accuracy
- Identify patterns and insights
- Create structured outlines for content
- Flag contradictions for human review
- Generate key takeaways and recommendations""",
        tools=["fact_checker", "outline_builder", "insight_extractor"],
        workspace_path="./workspace/analyst",
        heartbeat_interval=600,
    ),
    "writer": AgentRole(
        agent_id="agent:writer:main",
        role_name="Content Writer",
        model_config=ModelConfig(
            primary="llama-3.3-70b-versatile",
            fallbacks=["llama-3.1-8b-instant"],
            max_tokens=4096,
            temperature=0.7,
        ),
        system_prompt="""You are a professional content writer creating engaging, well-structured articles.
Your responsibilities:
- Write clear, compelling prose based on research and outlines
- Follow brand voice guidelines
- Structure content with proper headers and formatting
- Ensure readability and flow
- Maintain consistency in tone and style""",
        tools=["content_formatter", "style_checker", "header_generator"],
        workspace_path="./workspace/writer",
        heartbeat_interval=900,
    ),
    "seo_specialist": AgentRole(
        agent_id="agent:seo:main",
        role_name="SEO Specialist",
        model_config=ModelConfig(
            primary="llama-3.1-8b-instant",
            fallbacks=["llama-3.3-70b-versatile"],
            max_tokens=2048,
            temperature=0.3,
        ),
        system_prompt="""You are an SEO specialist optimizing content for search visibility.
Your responsibilities:
- Identify primary and secondary keywords
- Optimize meta descriptions and titles
- Improve readability scores
- Generate structured data markup
- Ensure keyword density is appropriate""",
        tools=["keyword_analyzer", "metadata_optimizer", "schema_generator"],
        workspace_path="./workspace/seo",
        heartbeat_interval=900,
    ),
    "quality_checker": AgentRole(
        agent_id="agent:quality:main",
        role_name="Quality Assurance",
        model_config=ModelConfig(
            primary="llama-3.3-70b-versatile",
            fallbacks=["llama-3.1-8b-instant"],
            max_tokens=2048,
            temperature=0.2,
        ),
        system_prompt="""You are a quality assurance specialist reviewing content before publication.
Your responsibilities:
- Check for grammar and spelling errors
- Verify factual accuracy
- Ensure content meets quality standards
- Validate SEO optimization
- Provide improvement recommendations""",
        tools=["grammar_checker", "fact_validator", "quality_scorer"],
        workspace_path="./workspace/quality",
        heartbeat_interval=900,
    ),
}

