from typing import Dict, Any, Callable
from .schemas import WorkflowDefinition, WorkflowInput

class WorkflowRegistry:
    def __init__(self):
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._executors: Dict[str, Callable] = {}

    def register_function(self, name: str, func: Callable, description: str = "", inputs: list = None):
        """
        Register a simple python function as a workflow.
        """
        workflow_id = name.lower() # simplify ID generation for now
        
        definition = WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description,
            inputs=inputs or []
        )
        
        self._workflows[workflow_id] = definition
        self._executors[workflow_id] = func
        return workflow_id

    def list_workflows(self) -> list[WorkflowDefinition]:
        return list(self._workflows.values())

    def get_executor(self, workflow_id: str) -> Callable:
        return self._executors.get(workflow_id)

    def get_definition(self, workflow_id: str) -> WorkflowDefinition:
        return self._workflows.get(workflow_id)
