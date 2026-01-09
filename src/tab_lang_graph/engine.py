import time
import asyncio
from typing import Any, Dict
from .registry import WorkflowRegistry
from .schemas import ExecutionRequest, ExecutionResponse

class ExecutionEngine:
    def __init__(self, registry: WorkflowRegistry):
        self.registry = registry
        self.is_paused = False

    async def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        start_time = time.time()
        
        if self.is_paused:
             return ExecutionResponse(
                request_id=request.request_id,
                status="pending", # In a real system this would go to a queue
                result=None,
                error_message="System is paused",
                execution_time_ms=0
            )

        executor = self.registry.get_executor(request.workflow_id)
        if not executor:
            return ExecutionResponse(
                request_id=request.request_id,
                status="error",
                result=None,
                error_message=f"Workflow '{request.workflow_id}' not found",
                execution_time_ms=(time.time() - start_time) * 1000
            )

        try:
            # Check if executor is async
            if asyncio.iscoroutinefunction(executor):
                result = await executor(**request.arguments)
            else:
                result = executor(**request.arguments)
                
            duration = (time.time() - start_time) * 1000
            return ExecutionResponse(
                request_id=request.request_id,
                status="success",
                result=result,
                execution_time_ms=duration
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ExecutionResponse(
                request_id=request.request_id,
                status="error",
                result=None,
                error_message=str(e),
                execution_time_ms=duration
            )

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False
