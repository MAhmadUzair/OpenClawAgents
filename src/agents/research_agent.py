"""Research agent for gathering and summarizing information."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List
import logging

from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Research-focused agent for information gathering."""

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task.

        Args:
            task: Task dictionary containing topic and parameters.

        Returns:
            Dictionary with research results including sources and summaries.
        """
        topic = task.get("topic", "")
        max_sources = task.get("max_sources", 5)
        task_id = task.get("id", "unknown")

        self.logger.info(f"Starting research on: {topic}")

        try:
            # Gather sources
            sources = await self._gather_sources(topic, max_sources)

            # Summarize sources
            summaries = await self._summarize_sources(sources, topic)

            # Create research report
            research_report = await self._create_research_report(
                topic, sources, summaries
            )

            result = {
                "task_id": task_id,
                "agent": self.agent_id,
                "status": "completed",
                "topic": topic,
                "sources_found": len(sources),
                "sources": sources,
                "summaries": summaries,
                "research_report": research_report,
                "timestamp": datetime.now().isoformat(),
            }

            self.update_session(task_id, "completed")
            self.save_task_result(task_id, result)

            self.logger.info(
                f"Research completed: {len(sources)} sources found"
            )
            return result

        except Exception as e:
            self.logger.error(f"Research task failed: {str(e)}")
            self.update_session(task_id, "failed")
            raise

    async def _gather_sources(
        self, topic: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Gather research sources on given topic.

        Args:
            topic: Research topic.
            limit: Maximum number of sources to gather.

        Returns:
            List of source dictionaries with title, url, and relevance.
        """
        # Simulate research with structured data
        # In production, this would call actual search APIs
        prompt = f"""Generate a list of {limit} credible research sources about: {topic}

For each source, provide:
- Title
- URL (use example.com format)
- Brief description
- Relevance score (0.0 to 1.0)

Format as JSON array."""

        try:
            response = await self.call_llm(prompt, max_tokens=2048)
            # Parse response and extract sources
            # For demo, we'll create structured sources
            sources = []
            for i in range(min(limit, 5)):
                sources.append(
                    {
                        "title": f"Research Source {i+1} on {topic}",
                        "url": f"https://example.com/research/{topic.replace(' ', '-').lower()}-{i+1}",
                        "description": f"Comprehensive information about {topic} covering key aspects and recent developments.",
                        "relevance": 0.9 - (i * 0.1),
                        "type": "article",
                    }
                )
            return sources
        except Exception as e:
            self.logger.warning(f"Source gathering had issues: {e}")
            # Return fallback sources
            return [
                {
                    "title": f"Primary Source on {topic}",
                    "url": f"https://example.com/{topic.replace(' ', '-')}",
                    "description": f"Authoritative source on {topic}",
                    "relevance": 0.95,
                    "type": "article",
                }
            ]

    async def _summarize_sources(
        self, sources: List[Dict[str, Any]], topic: str
    ) -> List[Dict[str, Any]]:
        """Summarize each research source.

        Args:
            sources: List of source dictionaries.
            topic: Research topic for context.

        Returns:
            List of summary dictionaries with key points.
        """
        summaries = []

        for source in sources:
            prompt = f"""Summarize the following research source about {topic}:

Title: {source['title']}
URL: {source['url']}
Description: {source.get('description', '')}

Provide:
1. Key findings (3-5 bullet points)
2. Important statistics or data points
3. Authoritative claims
4. Any contradictions or limitations

Format as structured summary."""

            try:
                summary_text = await self.call_llm(prompt, max_tokens=1024)
                summary = {
                    "source_url": source["url"],
                    "source_title": source["title"],
                    "summary": summary_text,
                    "key_points": self._extract_key_points(summary_text),
                    "relevance_score": source.get("relevance", 0.5),
                }
                summaries.append(summary)
            except Exception as e:
                self.logger.warning(f"Failed to summarize {source['url']}: {e}")
                summaries.append(
                    {
                        "source_url": source["url"],
                        "source_title": source["title"],
                        "summary": f"Summary of {source['title']}",
                        "key_points": ["Point 1", "Point 2", "Point 3"],
                        "relevance_score": source.get("relevance", 0.5),
                    }
                )

        return summaries

    def _extract_key_points(self, summary_text: str) -> List[str]:
        """Extract key points from summary text.

        Args:
            summary_text: Summary text to parse.

        Returns:
            List of key point strings.
        """
        # Simple extraction - in production would use more sophisticated parsing
        lines = summary_text.split("\n")
        key_points = []
        for line in lines:
            line = line.strip()
            if line and (
                line.startswith("-") or line.startswith("*") or line[0].isdigit()
            ):
                key_points.append(line)
            if len(key_points) >= 5:
                break
        return key_points[:5] if key_points else ["Key finding 1", "Key finding 2"]

    async def _create_research_report(
        self,
        topic: str,
        sources: List[Dict[str, Any]],
        summaries: List[Dict[str, Any]],
    ) -> str:
        """Create comprehensive research report.

        Args:
            topic: Research topic.
            sources: List of gathered sources.
            summaries: List of source summaries.

        Returns:
            Formatted research report as markdown.
        """
        prompt = f"""Create a comprehensive research report on: {topic}

Based on {len(sources)} sources gathered, synthesize the information into:
1. Executive Summary
2. Key Findings
3. Important Statistics
4. Trends and Patterns
5. Gaps in Current Research
6. Recommendations

Format as well-structured markdown document."""

        try:
            report = await self.call_llm(prompt, max_tokens=2048)
            return report
        except Exception as e:
            self.logger.error(f"Failed to create research report: {e}")
            return f"# Research Report: {topic}\n\nResearch completed with {len(sources)} sources."

