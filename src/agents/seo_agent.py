"""SEO agent for content optimization."""

import re
from datetime import datetime
from typing import Any, Dict, List
import logging

from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SEOAgent(BaseAgent):
    """SEO specialist agent for optimizing content."""

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SEO optimization task.

        Args:
            task: Task dictionary containing content to optimize.

        Returns:
            Dictionary with SEO optimization results.
        """
        content = task.get("content", "")
        topic = task.get("topic", "")
        task_id = task.get("id", "unknown")

        self.logger.info(f"Starting SEO optimization for topic: {topic}")

        try:
            # Analyze keywords
            keywords = await self._analyze_keywords(content, topic)

            # Optimize metadata
            metadata = await self._optimize_metadata(content, topic, keywords)

            # Improve content SEO
            optimized_content = await self._optimize_content(content, keywords)

            # Generate schema markup
            schema = await self._generate_schema(content, topic, metadata)

            # Calculate SEO score
            seo_score = self._calculate_seo_score(
                optimized_content, keywords, metadata
            )

            result = {
                "task_id": task_id,
                "agent": self.agent_id,
                "status": "completed",
                "keywords": keywords,
                "metadata": metadata,
                "optimized_content": optimized_content,
                "schema_markup": schema,
                "seo_score": seo_score,
                "recommendations": await self._generate_seo_recommendations(
                    optimized_content, keywords
                ),
                "timestamp": datetime.now().isoformat(),
            }

            self.update_session(task_id, "completed")
            self.save_task_result(task_id, result)

            self.logger.info(f"SEO optimization completed: Score {seo_score}/100")
            return result

        except Exception as e:
            self.logger.error(f"SEO task failed: {str(e)}")
            self.update_session(task_id, "failed")
            raise

    async def _analyze_keywords(
        self, content: str, topic: str
    ) -> Dict[str, Any]:
        """Analyze and extract keywords from content.

        Args:
            content: Content to analyze.
            topic: Main topic.

        Returns:
            Dictionary with keyword analysis.
        """
        prompt = f"""Analyze the following content and identify SEO keywords:

Topic: {topic}
Content: {content[:1500]}...

Identify:
1. Primary keyword (main topic)
2. Secondary keywords (3-5 related terms)
3. Long-tail keywords (2-3 phrases)
4. Keyword density for each
5. LSI (Latent Semantic Indexing) keywords

Format as structured analysis."""

        try:
            analysis = await self.call_llm(prompt, max_tokens=1024)
            # Extract keywords from analysis
            primary = topic.lower()
            secondary = self._extract_keywords_from_text(analysis, 5)
            long_tail = self._extract_long_tail_keywords(content, topic)

            return {
                "primary": primary,
                "secondary": secondary,
                "long_tail": long_tail,
                "density": self._calculate_keyword_density(content, primary),
                "analysis": analysis,
            }
        except Exception as e:
            self.logger.warning(f"Keyword analysis had issues: {e}")
            return {
                "primary": topic.lower(),
                "secondary": [topic.lower() + " guide", topic.lower() + " tips"],
                "long_tail": [f"best {topic.lower()}", f"how to {topic.lower()}"],
                "density": 2.5,
                "analysis": "Keyword analysis completed",
            }

    def _extract_keywords_from_text(self, text: str, limit: int) -> List[str]:
        """Extract keywords from text.

        Args:
            text: Text to extract from.
            limit: Maximum number of keywords.

        Returns:
            List of keyword strings.
        """
        # Simple extraction - look for quoted terms or listed items
        keywords = []
        words = re.findall(r'"([^"]+)"', text)
        keywords.extend(words[:limit])

        # Also look for numbered lists
        lines = text.split("\n")
        for line in lines:
            if line.strip() and (line[0].isdigit() or line.startswith("-")):
                keyword = line.split(":", 1)[0].lstrip("0123456789.- ")
                if keyword and len(keyword) > 3:
                    keywords.append(keyword.lower())
                if len(keywords) >= limit:
                    break

        return keywords[:limit] if keywords else ["keyword1", "keyword2", "keyword3"]

    def _extract_long_tail_keywords(self, content: str, topic: str) -> List[str]:
        """Extract long-tail keywords.

        Args:
            content: Content text.
            topic: Main topic.

        Returns:
            List of long-tail keyword phrases.
        """
        topic_lower = topic.lower()
        return [
            f"comprehensive guide to {topic_lower}",
            f"everything about {topic_lower}",
            f"{topic_lower} best practices",
        ]

    def _calculate_keyword_density(self, content: str, keyword: str) -> float:
        """Calculate keyword density percentage.

        Args:
            content: Content text.
            keyword: Keyword to count.

        Returns:
            Keyword density as percentage.
        """
        words = content.lower().split()
        keyword_lower = keyword.lower()
        count = sum(1 for word in words if keyword_lower in word)
        total_words = len(words)
        return round((count / total_words * 100) if total_words > 0 else 0, 2)

    async def _optimize_metadata(
        self, content: str, topic: str, keywords: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize meta title and description.

        Args:
            content: Content text.
            topic: Main topic.
            keywords: Keyword analysis.

        Returns:
            Dictionary with optimized metadata.
        """
        primary_keyword = keywords.get("primary", topic)
        content_preview = content[:200].replace("\n", " ")

        prompt = f"""Create optimized SEO metadata:

Topic: {topic}
Primary Keyword: {primary_keyword}
Content Preview: {content_preview}...

Generate:
1. Meta Title (50-60 characters, include primary keyword)
2. Meta Description (150-160 characters, compelling and keyword-rich)
3. Open Graph Title
4. Open Graph Description

Format as structured metadata."""

        try:
            metadata_text = await self.call_llm(prompt, max_tokens=512)
            return {
                "title": self._extract_meta_field(metadata_text, "Title", 60),
                "description": self._extract_meta_field(
                    metadata_text, "Description", 160
                ),
                "og_title": self._extract_meta_field(metadata_text, "OG Title", 60),
                "og_description": self._extract_meta_field(
                    metadata_text, "OG Description", 160
                ),
                "raw": metadata_text,
            }
        except Exception as e:
            self.logger.warning(f"Metadata optimization had issues: {e}")
            return {
                "title": f"{topic} - Complete Guide",
                "description": f"Learn everything about {topic} with this comprehensive guide.",
                "og_title": f"{topic} Guide",
                "og_description": f"Complete guide to {topic}",
            }

    def _extract_meta_field(
        self, text: str, field_name: str, max_length: int
    ) -> str:
        """Extract meta field from text.

        Args:
            text: Text to extract from.
            field_name: Name of field to extract.
            max_length: Maximum length of field.

        Returns:
            Extracted field value.
        """
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if field_name.lower() in line.lower():
                # Get the next line or current line content
                if ":" in line:
                    value = line.split(":", 1)[1].strip()
                elif i + 1 < len(lines):
                    value = lines[i + 1].strip()
                else:
                    value = line.strip()
                return value[:max_length]
        return f"{field_name} placeholder"

    async def _optimize_content(
        self, content: str, keywords: Dict[str, Any]
    ) -> str:
        """Optimize content for SEO.

        Args:
            content: Original content.
            keywords: Keyword analysis.

        Returns:
            SEO-optimized content.
        """
        primary = keywords.get("primary", "")
        secondary = keywords.get("secondary", [])

        # Ensure primary keyword in first paragraph
        lines = content.split("\n")
        optimized_lines = []

        for i, line in enumerate(lines):
            if i == 0 and primary and primary not in line.lower():
                # Add primary keyword to first heading or paragraph
                if line.startswith("#"):
                    optimized_lines.append(line)
                else:
                    optimized_lines.append(
                        line.replace(
                            line.split()[0] if line.split() else "",
                            f"{primary.title()} {line.split()[0] if line.split() else ''}",
                            1,
                        )
                    )
            else:
                optimized_lines.append(line)

        return "\n".join(optimized_lines)

    async def _generate_schema(
        self, content: str, topic: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate JSON-LD schema markup.

        Args:
            content: Content text.
            topic: Main topic.
            metadata: Metadata dictionary.

        Returns:
            Schema markup dictionary.
        """
        word_count = len(content.split())
        reading_time = round(word_count / 200.0, 1)

        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": metadata.get("title", topic),
            "description": metadata.get("description", ""),
            "articleBody": content[:500],
            "wordCount": word_count,
            "timeRequired": f"PT{int(reading_time)}M",
            "author": {
                "@type": "Organization",
                "name": "Content Team",
            },
        }

    def _calculate_seo_score(
        self, content: str, keywords: Dict[str, Any], metadata: Dict[str, Any]
    ) -> int:
        """Calculate overall SEO score.

        Args:
            content: Content text.
            keywords: Keyword analysis.
            metadata: Metadata dictionary.

        Returns:
            SEO score out of 100.
        """
        score = 0

        # Title optimization (20 points)
        title = metadata.get("title", "")
        if title and 50 <= len(title) <= 60:
            score += 20
        elif title:
            score += 10

        # Description optimization (20 points)
        desc = metadata.get("description", "")
        if desc and 150 <= len(desc) <= 160:
            score += 20
        elif desc:
            score += 10

        # Keyword density (20 points)
        density = keywords.get("density", 0)
        if 1.0 <= density <= 3.0:
            score += 20
        elif 0.5 <= density <= 4.0:
            score += 10

        # Content length (20 points)
        word_count = len(content.split())
        if 1000 <= word_count <= 3000:
            score += 20
        elif 500 <= word_count <= 5000:
            score += 10

        # Headings structure (20 points)
        headings = len(re.findall(r"^#+\s", content, re.MULTILINE))
        if 3 <= headings <= 10:
            score += 20
        elif headings > 0:
            score += 10

        return min(score, 100)

    async def _generate_seo_recommendations(
        self, content: str, keywords: Dict[str, Any]
    ) -> List[str]:
        """Generate SEO improvement recommendations.

        Args:
            content: Content text.
            keywords: Keyword analysis.

        Returns:
            List of recommendation strings.
        """
        recommendations = []

        density = keywords.get("density", 0)
        if density < 1.0:
            recommendations.append("Increase primary keyword density")
        elif density > 3.0:
            recommendations.append("Reduce keyword density to avoid over-optimization")

        word_count = len(content.split())
        if word_count < 1000:
            recommendations.append("Expand content to at least 1000 words")
        elif word_count > 3000:
            recommendations.append("Consider breaking into multiple articles")

        headings = len(re.findall(r"^#+\s", content, re.MULTILINE))
        if headings < 3:
            recommendations.append("Add more section headings for better structure")

        return recommendations

