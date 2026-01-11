from fastapi import FastAPI, HTTPException
from typing import List
from .registry import WorkflowRegistry
from .engine import ExecutionEngine
from .schemas import ExecutionRequest, ExecutionResponse, BridgeStatus
from .config import settings
from .library import setup_library
from .tasks import TaskManager, TaskStatus, Task

app = FastAPI(title="TabLangGraph Bridge")

# Singleton instances (for now)
registry = WorkflowRegistry()
setup_library(registry)

engine = ExecutionEngine(registry)
task_manager = TaskManager()
execution_history: List[ExecutionResponse] = []

# Register a default echo workflow for testing
def echo_workflow(text: str):
    return f"Echo: {text}"

registry.register_function(
    name="Echo",
    func=echo_workflow,
    description="Simple echo for testing connection",
    inputs=[{"name": "text", "type": "string"}]
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/workflows")
async def list_workflows():
    return registry.list_workflows()

@app.post("/execute", response_model=ExecutionResponse)
async def execute_workflow(request: ExecutionRequest):
    # 1. Check Function Complexity
    workflow_def = registry.get_definition(request.workflow_id)
    complexity = "quick"
    if workflow_def and workflow_def.metadata:
        complexity = workflow_def.metadata.get("complexity", "quick")

    # 2. If Heavy, Delegate to Task Manager
    if complexity == "heavy":
        # Check if a task already exists for these inputs
        existing_task = task_manager.find_existing_task(
            request.workflow_id, 
            request.positional_args, 
            request.arguments
        )

        if existing_task:
            if existing_task.status == TaskStatus.COMPLETED:
                # Return the result if done
                return ExecutionResponse(
                    request_id=request.request_id,
                    status="success",
                    result=existing_task.result
                )
            elif existing_task.status == TaskStatus.FAILED:
                 return ExecutionResponse(
                    request_id=request.request_id,
                    status="error",
                    error_message=f"Task Failed: {existing_task.error}"
                )
            else:
                # Return status message
                return ExecutionResponse(
                    request_id=request.request_id,
                    status="success", # Success because we successfully checked status
                    result=f"Version 1: (Please Refresh) Task Status: {existing_task.status.value} (ID: {existing_task.task_id[:8]})"
                )
        else:
            # Create new task
            new_task = task_manager.create_task(
                request.workflow_id,
                request.positional_args,
                request.arguments
            )
            return ExecutionResponse(
                request_id=request.request_id,
                status="success",
                result=f"Action Required: Heavy Task Created. Please Approve in Management UI. (ID: {new_task.task_id[:8]})"
            )

    # 3. If Quick, Execute Immediately
    response = await engine.execute(request)
    # Log to history
    execution_history.append(response)
    return response

@app.get("/tasks", response_model=List[Task])
async def list_tasks():
    return task_manager.list_tasks()

@app.post("/tasks/{task_id}/approve")
async def approve_task(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update status to RUNNING immediately for UI feedback
    task_manager.update_status(task_id, TaskStatus.RUNNING)
    
    # Execute (In a real app, send to background worker queue)
    # Here we await it, but since it's "heavy" it might block slightly if we don't async it properly
    # For now, let's run it.
    
    # Reconstruct execution request
    req = ExecutionRequest(
        workflow_id=task.workflow_id,
        positional_args=task.positional_args,
        arguments=task.arguments
    )
    
    # Run
    try:
        resp = await engine.execute(req)
        if resp.status == "success":
            task_manager.update_status(task_id, TaskStatus.COMPLETED, result=resp.result)
        else:
            task_manager.update_status(task_id, TaskStatus.FAILED, error=resp.error_message)
    except Exception as e:
        task_manager.update_status(task_id, TaskStatus.FAILED, error=str(e))
        
    return {"status": "ok"}

@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    task_manager.update_status(task_id, TaskStatus.CANCELLED)
    return {"status": "ok"}

@app.get("/history", response_model=List[ExecutionResponse])
async def get_history():
    return execution_history

@app.get("/status", response_model=BridgeStatus)
async def get_status():
    return BridgeStatus(
        status="paused" if engine.is_paused else "active",
        active_models=[],
        queue_size=0
    )

@app.post("/control")
async def control(action: str):
    if action == "pause":
        engine.pause()
    elif action == "resume":
        engine.resume()
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    return {"status": "ok"}
