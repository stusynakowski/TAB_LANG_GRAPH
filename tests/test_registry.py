import pytest
from fancy_sheet_functions.registry import WorkflowRegistry
from fancy_sheet_functions.schemas import WorkflowDefinition

def test_registry_initialization():
    registry = WorkflowRegistry()
    assert registry.list_workflows() == []

def test_register_function():
    registry = WorkflowRegistry()
    
    def sample_func(x):
        return x * 2
        
    registry.register_function(
        name="Double",
        func=sample_func,
        description="Doubles input",
        inputs=[{"name": "x", "type": "number"}]
    )
    
    workflows = registry.list_workflows()
    assert len(workflows) == 1
    assert workflows[0].name == "Double"
    assert workflows[0].id == "double"

def test_get_executor():
    registry = WorkflowRegistry()
    def sample_func(x):
        return x
    
    registry.register_function("Identity", sample_func)
    executor = registry.get_executor("identity")
    assert executor == sample_func
    
def test_get_executor_not_found():
    registry = WorkflowRegistry()
    executor = registry.get_executor("missing")
    assert executor is None
