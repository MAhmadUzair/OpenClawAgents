"""Main execution entry point for OpenClawAgents content pipeline."""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import EnvironmentConfig
from src.workflow.workflow_engine import WorkflowEngine

# Setup logging
logging.basicConfig(
    level=getattr(logging, EnvironmentConfig.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("openclaw_agents.log"),
    ],
)

logger = logging.getLogger(__name__)


async def main():
    """Main execution point."""
    # Get API key from environment
    api_key = EnvironmentConfig.GROQ_API_KEY
    if not api_key:
        logger.error(
            "GROQ_API_KEY environment variable not set. "
            "Please set it in your .env file or environment."
        )
        logger.info("You can create a .env file with: GROQ_API_KEY=your_key_here")
        return

    # Initialize workflow engine
    logger.info("Initializing OpenClawAgents workflow engine...")
    engine = WorkflowEngine(api_key)

    # Example: Run content pipeline
    topic = "Artificial Intelligence in Healthcare 2025"
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])

    logger.info(f"Starting content pipeline for topic: {topic}")
    logger.info("=" * 60)

    try:
        # Execute pipeline
        pipeline_results = await engine.run_content_pipeline(topic)

        # Display results
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE EXECUTION COMPLETE")
        logger.info("=" * 60)

        pipeline = pipeline_results["pipeline"]
        results = pipeline_results["results"]

        logger.info(f"\nPipeline ID: {pipeline['pipeline_id']}")
        logger.info(f"Topic: {pipeline['topic']}")
        logger.info(f"Iterations: {pipeline_results['iterations']}")

        logger.info("\nTask Results:")
        logger.info("-" * 60)

        for task_name, task_id in pipeline["tasks"].items():
            task_result = results.get(task_id, {})
            status = task_result.get("status", "unknown")
            logger.info(f"{task_name.upper()}: {status}")

            if status == "completed":
                # Show key metrics
                if task_name == "research":
                    sources = task_result.get("sources_found", 0)
                    logger.info(f"  - Sources found: {sources}")
                elif task_name == "writing":
                    word_count = task_result.get("word_count", 0)
                    logger.info(f"  - Word count: {word_count}")
                elif task_name == "seo":
                    seo_score = task_result.get("seo_score", 0)
                    logger.info(f"  - SEO Score: {seo_score}/100")
                elif task_name == "quality":
                    quality_score = task_result.get("quality_score", 0)
                    approved = task_result.get("approved", False)
                    logger.info(f"  - Quality Score: {quality_score}/100")
                    logger.info(f"  - Approved: {approved}")

        # Save final report
        report_file = Path(EnvironmentConfig.WORKSPACE_DIR) / "pipeline_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(pipeline_results, f, indent=2, default=str)

        logger.info(f"\nFull report saved to: {report_file}")

        # Display content preview if available
        writing_task_id = pipeline["tasks"].get("writing")
        if writing_task_id and writing_task_id in results:
            content = results[writing_task_id].get("content", "")
            if content:
                logger.info("\n" + "=" * 60)
                logger.info("CONTENT PREVIEW")
                logger.info("=" * 60)
                preview = content[:500] + "..." if len(content) > 500 else content
                logger.info(preview)

    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nPipeline execution interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

