"""
FastAPI server for AutoPlayTest
Provides REST API endpoints for running tests
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import uuid
from datetime import datetime
import os

from src.simple_runner import run_test_suite, generate_test_scripts, execute_test_scripts

app = FastAPI(
    title="AutoPlayTest API",
    description="AI-powered Playwright testing engine API",
    version="0.1.0"
)

# In-memory task storage (use Redis or database in production)
tasks: Dict[str, Dict[str, Any]] = {}


class TestRequest(BaseModel):
    """Test execution request model"""
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    test_types: Optional[List[str]] = None
    browser: str = "chromium"
    headless: bool = True
    timeout: int = 30000


class TaskResponse(BaseModel):
    """Task response model"""
    task_id: str
    status: str
    created_at: str
    message: str


class TaskStatus(BaseModel):
    """Task status model"""
    task_id: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


async def run_tests_background(task_id: str, request: TestRequest):
    """Background task to run tests"""
    try:
        tasks[task_id]["status"] = "running"
        tasks[task_id]["started_at"] = datetime.now().isoformat()
        
        # Run the test suite
        results = await run_test_suite(
            url=request.url,
            username=request.username,
            password=request.password,
            test_types=request.test_types,
            browser=request.browser,
            headless=request.headless,
            timeout=request.timeout
        )
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["completed_at"] = datetime.now().isoformat()
        tasks[task_id]["result"] = results
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["completed_at"] = datetime.now().isoformat()
        tasks[task_id]["error"] = str(e)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AutoPlayTest API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "run_tests": "/api/v1/tests/run",
            "generate_scripts": "/api/v1/tests/generate",
            "task_status": "/api/v1/tasks/{task_id}",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_providers": {
            "claude": bool(os.getenv("ANTHROPIC_API_KEY")),
            "gpt": bool(os.getenv("OPENAI_API_KEY")),
            "gemini": bool(os.getenv("GOOGLE_API_KEY"))
        }
    }


@app.post("/api/v1/tests/run", response_model=TaskResponse)
async def run_tests(
    request: TestRequest,
    background_tasks: BackgroundTasks
):
    """
    Run tests asynchronously
    
    This endpoint starts a background task to run the test suite
    and returns a task ID for tracking progress.
    """
    task_id = str(uuid.uuid4())
    
    # Initialize task
    tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "request": request.dict()
    }
    
    # Add background task
    background_tasks.add_task(run_tests_background, task_id, request)
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        created_at=tasks[task_id]["created_at"],
        message="Test execution started"
    )


@app.post("/api/v1/tests/generate")
async def generate_scripts(request: TestRequest):
    """
    Generate test scripts without executing them
    
    Returns the generated test scripts as JSON
    """
    try:
        scripts_path = await generate_test_scripts(
            url=request.url,
            username=request.username,
            password=request.password,
            test_types=request.test_types,
            output_dir=f"/tmp/autoplaytest_{uuid.uuid4()}"
        )
        
        # Read generated scripts
        scripts = []
        import os
        from pathlib import Path
        
        scripts_dir = Path(scripts_path)
        for script_file in scripts_dir.glob("test_*.py"):
            with open(script_file, 'r') as f:
                scripts.append({
                    "filename": script_file.name,
                    "content": f.read()
                })
        
        return {
            "status": "success",
            "scripts_path": scripts_path,
            "scripts": scripts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of a test execution task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    return TaskStatus(**task)


@app.delete("/api/v1/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running task (not implemented in this example)"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if tasks[task_id]["status"] != "running":
        raise HTTPException(status_code=400, detail="Task is not running")
    
    # In a real implementation, you would cancel the async task
    # For this example, we'll just mark it as cancelled
    tasks[task_id]["status"] = "cancelled"
    tasks[task_id]["completed_at"] = datetime.now().isoformat()
    
    return {"message": "Task cancelled", "task_id": task_id}


@app.get("/api/v1/tasks")
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 100
):
    """List all tasks with optional status filter"""
    task_list = list(tasks.values())
    
    if status:
        task_list = [t for t in task_list if t["status"] == status]
    
    # Sort by created_at descending
    task_list.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "tasks": task_list[:limit],
        "total": len(task_list),
        "limit": limit
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )