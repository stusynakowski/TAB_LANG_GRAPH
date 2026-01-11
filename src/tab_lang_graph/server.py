from fastapi import FastAPI, HTTPException
from typing import List
from .registry import WorkflowRegistry
from .engine import ExecutionEngine
from .schemas import ExecutionRequest, ExecutionResponse, BridgeStatus
from .config import settings
from .library import setup_library

app = FastAPI(title="TabLangGraph Bridge")

# Singleton instances (for now)
registry = WorkflowRegistry()
setup_library(registry)

engine = ExecutionEngine(registry)
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
    response = await engine.execute(request)
    # Log to history
    execution_history.append(response)
    return response

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
