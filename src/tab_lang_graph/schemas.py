from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class WorkflowInput(BaseModel):
    name: str
    type: str

class WorkflowDefinition(BaseModel):
    id: str
    name: str
    description: str
    inputs: List[WorkflowInput]

class ExecutionRequest(BaseModel):
    workflow_id: str
    arguments: Dict[str, Any]
    cell_reference: Optional[str] = None
    request_id: str = Field(default_factory=lambda: str(uuid4()))

class ExecutionResponse(BaseModel):
    request_id: str
    status: str # "success" | "error" | "pending"
    result: Any
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0

class BridgeStatus(BaseModel):
    status: str # "active" | "paused"
    active_models: List[str]
    queue_size: int
