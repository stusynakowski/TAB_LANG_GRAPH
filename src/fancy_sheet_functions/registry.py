from typing import Dict, Any, Callable
from .schemas import WorkflowDefinition, WorkflowInput
import inspect

class WorkflowRegistry:
    def __init__(self):
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._executors: Dict[str, Callable] = {}

    def register_function(self, name: str, func: Callable, description: str = "", inputs: list = None, metadata: Dict[str, Any] = None):
        """
        Register a simple python function as a workflow.
        """
        workflow_id = name.lower() # simplify ID generation for now
        
        if inputs is None:
            inputs = []
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                if param_name == 'self': continue
                param_type = "string" # default
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == int:
                        param_type = "number"
                    elif param.annotation == float:
                        param_type = "number"
                    elif param.annotation == bool:
                        param_type = "boolean"
                    elif param.annotation == str:
                        param_type = "string"
                    elif param.annotation == list:
                        param_type = "array"
                    elif param.annotation == dict:
                        param_type = "object"
                
                inputs.append({"name": param_name, "type": param_type})

        definition = WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description,
            inputs=inputs or [],
            metadata=metadata or {}
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
