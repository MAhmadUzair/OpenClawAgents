"""Main execution entry point for OpenClawAgents content pipeline API."""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

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

app = FastAPI(title="OpenClawAgents API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global workflow engine
workflow_engine: Optional[WorkflowEngine] = None


class PipelineRequest(BaseModel):
    topic: str


class PipelineResponse(BaseModel):
    pipeline_id: str
    topic: str
    status: str
    tasks: dict


@app.on_event("startup")
async def startup_event():
    """Initialize workflow engine on startup."""
    global workflow_engine
    api_key = EnvironmentConfig.GROQ_API_KEY
    if not api_key:
        logger.error("GROQ_API_KEY not set")
        return
    workflow_engine = WorkflowEngine(api_key)
    logger.info("Workflow engine initialized")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "OpenClawAgents API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "engine_ready": workflow_engine is not None}


@app.post("/api/pipeline/run", response_model=PipelineResponse)
async def run_pipeline(request: PipelineRequest):
    """Run content pipeline for given topic."""
    if not workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow engine not initialized")
    
    try:
        logger.info(f"Starting pipeline for topic: {request.topic}")
        results = await workflow_engine.run_content_pipeline(request.topic)
        
        pipeline = results["pipeline"]
        task_results = results["results"]
        
        # Get task statuses
        task_statuses = {}
        for task_name, task_id in pipeline["tasks"].items():
            task = workflow_engine.task_queue.get_task(task_id)
            if task:
                task_statuses[task_name] = {
                    "id": task_id,
                    "status": task.status.value,
                    "title": task.title
                }
        
        return PipelineResponse(
            pipeline_id=pipeline["pipeline_id"],
            topic=pipeline["topic"],
            status="completed",
            tasks=task_statuses
        )
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pipeline/{pipeline_id}/status")
async def get_pipeline_status(pipeline_id: str):
    """Get pipeline status."""
    if not workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow engine not initialized")
    
    status = workflow_engine.get_pipeline_status(pipeline_id)
    return status


@app.get("/api/pipeline/{pipeline_id}/results")
async def get_pipeline_results(pipeline_id: str):
    """Get pipeline results."""
    if not workflow_engine:
        raise HTTPException(status_code=503, detail="Workflow engine not initialized")
    
    # Get all tasks and their results
    all_tasks = workflow_engine.task_queue._load_all_tasks()
    results = {}
    
    for task in all_tasks:
        if task.result:
            results[task.id] = {
                "title": task.title,
                "status": task.status.value,
                "result": task.result
            }
    
    return {"pipeline_id": pipeline_id, "results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
