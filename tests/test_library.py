import pytest
from fancy_sheet_functions.registry import WorkflowRegistry
from fancy_sheet_functions.library import setup_library, to_upper

def test_library_registration():
    registry = WorkflowRegistry()
    setup_library(registry)
    
    # Check if functions were registered
    workflows = registry.list_workflows()
    workflow_ids = [w.id for w in workflows]
    
    assert "toupper" in workflow_ids
    assert "tolower" in workflow_ids
    assert "concatenate" in workflow_ids
    assert "llm_sumarize_test" in workflow_ids

def test_introspection():
    registry = WorkflowRegistry()
    setup_library(registry)
    
    # Check definition of ToUpper
    to_upper_def = registry.get_definition("toupper")
    assert to_upper_def is not None
    assert to_upper_def.name == "ToUpper"
    assert len(to_upper_def.inputs) == 1
    assert to_upper_def.inputs[0].name == "text"
    assert to_upper_def.inputs[0].type == "string"

    # Check definition of Sum
    sum_def = registry.get_definition("sum")
    assert sum_def is not None
    assert len(sum_def.inputs) == 2
    assert sum_def.inputs[0].type == "number"
