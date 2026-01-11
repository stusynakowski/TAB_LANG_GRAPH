import pytest
import asyncio
from fancy_sheet_functions.engine import ExecutionEngine
from fancy_sheet_functions.registry import WorkflowRegistry
from fancy_sheet_functions.schemas import ExecutionRequest

@pytest.mark.asyncio
async def test_execution_synch_success():
    registry = WorkflowRegistry()
    registry.register_function("Echo", lambda text: f"Echo: {text}")
    
    engine = ExecutionEngine(registry)
    req = ExecutionRequest(
        workflow_id="echo",
        arguments={"text": "Hello"}
    )
    
    response = await engine.execute(req)
    assert response.status == "success"
    assert response.result == "Echo: Hello"
    assert response.request_id == req.request_id

@pytest.mark.asyncio
async def test_execution_async_success():
    registry = WorkflowRegistry()
    
    async def async_double(n):
        await asyncio.sleep(0.01)
        return n * 2
        
    registry.register_function("Double", async_double)
    
    engine = ExecutionEngine(registry)
    req = ExecutionRequest(
        workflow_id="double",
        arguments={"n": 5}
    )
    
    response = await engine.execute(req)
    assert response.status == "success"
    assert response.result == 10

@pytest.mark.asyncio
async def test_execution_not_found():
    registry = WorkflowRegistry()
    engine = ExecutionEngine(registry)
    req = ExecutionRequest(workflow_id="missing", arguments={})
    
    response = await engine.execute(req)
    assert response.status == "error"
    assert "not found" in response.error_message

@pytest.mark.asyncio
async def test_execution_error_in_workflow():
    registry = WorkflowRegistry()
    def failing_func():
        raise ValueError("Boom")
        
    registry.register_function("Fail", failing_func)
    
    engine = ExecutionEngine(registry)
    req = ExecutionRequest(workflow_id="fail", arguments={})
    
    response = await engine.execute(req)
    assert response.status == "error"
    assert "Boom" in response.error_message

@pytest.mark.asyncio
async def test_pause_resume():
    registry = WorkflowRegistry()
    registry.register_function("Echo", lambda x: x)
    
    engine = ExecutionEngine(registry)
    req = ExecutionRequest(workflow_id="echo", arguments={"x": 1})
    
    # Normal run
    res1 = await engine.execute(req)
    assert res1.status == "success"
    
    # Pause
    engine.pause()
    res2 = await engine.execute(req)
    assert res2.status == "pending"
    assert res2.error_message == "System is paused"
    
    # Resume
    engine.resume()
    res3 = await engine.execute(req)
    assert res3.status == "success"
