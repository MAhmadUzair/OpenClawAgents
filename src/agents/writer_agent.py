"""Writer agent for content generation."""

from datetime import datetime
from typing import Any, Dict
import logging

from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """Content writing agent for generating articles."""

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute writing task.

        Args:
            task: Task dictionary containing outline and style guide.

        Returns:
            Dictionary with generated content.
        """
        outline = task.get("outline", {})
        style_guide = task.get("style_guide", "professional")
        research_data = task.get("research_data", {})
        task_id = task.get("id", "unknown")
        
        # Extract topic from research data or outline
        topic = research_data.get("topic", "") or outline.get("title", "").replace("Comprehensive Guide to ", "").replace("Guide to ", "")

        self.logger.info(f"Starting content writing with style: {style_guide}, topic: {topic}")

        try:
            # Generate content from outline
            content = await self._generate_content(outline, style_guide, research_data, topic)

            # Format content
            formatted_content = await self._format_content(content)

            # Calculate metrics
            word_count = len(formatted_content.split())
            reading_time = self._calculate_reading_time(word_count)

            result = {
                "task_id": task_id,
                "agent": self.agent_id,
                "status": "completed",
                "content": formatted_content,
                "word_count": word_count,
                "reading_time_minutes": reading_time,
                "style": style_guide,
                "topic": topic,
                "timestamp": datetime.now().isoformat(),
            }

            self.update_session(task_id, "completed")
            self.save_task_result(task_id, result)

            self.logger.info(f"Content written: {word_count} words")
            return result

        except Exception as e:
            self.logger.error(f"Writing task failed: {str(e)}")
            self.update_session(task_id, "failed")
            raise

    async def _generate_content(
        self,
        outline: Dict[str, Any],
        style: str,
        research_data: Dict[str, Any],
        topic: str = "",
    ) -> str:
        """Generate content from outline.

        Args:
            outline: Content outline dictionary.
            style: Writing style guide.
            research_data: Research data for context.
            topic: Main topic of the article.

        Returns:
            Generated content as markdown string.
        """
        title = outline.get("title", f"Article about {topic}" if topic else "Article")
        if "Unknown" in title or not title.strip():
            title = f"Comprehensive Guide to {topic}" if topic else "Article"
        
        sections = outline.get("sections", [])
        introduction = outline.get("introduction", {})

        # Extract key research points
        research_summary = ""
        if research_data:
            if research_data.get("research_report"):
                research_summary = research_data["research_report"][:1000]
            elif research_data.get("summaries"):
                research_summary = "\n".join([
                    s.get("summary", "")[:200] for s in research_data["summaries"][:3]
                ])
        
        prompt = f"""Write a comprehensive article about {topic if topic else 'the topic'} based on the following outline:

Title: {title}

Introduction:
- Hook: {introduction.get('hook', f'Exploring {topic}' if topic else 'Introduction')}
- Thesis: {introduction.get('thesis', f'Key insights about {topic}' if topic else 'Main thesis')}
- Overview: {introduction.get('overview', f'This article covers essential aspects of {topic}' if topic else 'Overview')}

Sections:
{self._format_sections_for_prompt(sections)}

Style Guide: {style}
- Use clear, engaging prose
- Maintain professional tone
- Include relevant examples
- Use proper markdown formatting
- Ensure smooth transitions between sections
- Focus specifically on {topic if topic else 'the topic'}

Research Context: {research_summary[:1000] if research_summary else 'Research data available'}

Write the complete article in markdown format with proper headings, paragraphs, and formatting. Make sure the content is specifically about {topic if topic else 'the topic'} and not generic."""

        try:
            content = await self.call_llm(prompt, max_tokens=4096)
            return content
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            # Return fallback content
            return self._generate_fallback_content(outline)

    def _format_sections_for_prompt(self, sections: list) -> str:
        """Format sections for prompt.

        Args:
            sections: List of section dictionaries.

        Returns:
            Formatted string of sections.
        """
        formatted = []
        for i, section in enumerate(sections, 1):
            title = section.get("title", f"Section {i}")
            subsections = section.get("subsections", [])
            formatted.append(f"{i}. {title}")
            for j, sub in enumerate(subsections, 1):
                formatted.append(f"   {i}.{j} {sub}")
        return "\n".join(formatted)

    def _generate_fallback_content(self, outline: Dict[str, Any]) -> str:
        """Generate fallback content if LLM fails.

        Args:
            outline: Content outline.

        Returns:
            Basic markdown content.
        """
        title = outline.get("title", "Article")
        sections = outline.get("sections", [])

        content = f"# {title}\n\n"
        content += "## Introduction\n\n"
        content += "This article explores the topic in detail.\n\n"

        for section in sections:
            content += f"## {section.get('title', 'Section')}\n\n"
            content += "This section covers important aspects of the topic.\n\n"

        content += "## Conclusion\n\n"
        content += "In summary, this topic has significant implications.\n"

        return content

    async def _format_content(self, content: str) -> str:
        """Format content with proper markdown.

        Args:
            content: Raw content string.

        Returns:
            Formatted markdown content.
        """
        # Ensure proper markdown formatting
        lines = content.split("\n")
        formatted_lines = []
        prev_empty = False

        for line in lines:
            line = line.rstrip()
            if not line:
                if not prev_empty:
                    formatted_lines.append("")
                    prev_empty = True
            else:
                formatted_lines.append(line)
                prev_empty = False

        return "\n".join(formatted_lines).strip()

    def _calculate_reading_time(self, word_count: int) -> float:
        """Calculate reading time in minutes.

        Args:
            word_count: Number of words.

        Returns:
            Reading time in minutes.
        """
        # Average reading speed: 200 words per minute
        return round(word_count / 200.0, 1)

