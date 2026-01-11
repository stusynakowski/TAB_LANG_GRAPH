from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
import uuid

class TaskStatus(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"  # Ready to run
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task(BaseModel):
    task_id: str
    workflow_id: str
    arguments: Dict[str, Any]
    positional_args: List[Any]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    result: Optional[Any] = None
    error: Optional[str] = None

class TaskManager:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    def _generate_task_key(self, workflow_id: str, args: List[Any], kwargs: Dict[str, Any]) -> str:
        # Create a deterministic key based on inputs to properly find existing tasks for the same call
        # This is a simple implementation, might need better serialization for complex objects
        return f"{workflow_id}:{str(args)}:{str(kwargs)}"

    def find_existing_task(self, workflow_id: str, args: List[Any], kwargs: Dict[str, Any]) -> Optional[Task]:
        # In a real DB we would query. Here we check linearly or use a key map.
        # Since we want to return the EXACT SAME task if the user re-executes the cell:
        target_key = self._generate_task_key(workflow_id, args, kwargs)
        # Check all tasks (inefficient for prod, fine for MVP)
        for task in self._tasks.values():
            key = self._generate_task_key(task.workflow_id, task.positional_args, task.arguments)
            if key == target_key:
                return task
        return None

    def create_task(self, workflow_id: str, args: List[Any], kwargs: Dict[str, Any]) -> Task:
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            workflow_id=workflow_id,
            positional_args=args,
            arguments=kwargs,
            status=TaskStatus.PENDING_APPROVAL,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_tasks(self) -> List[Task]:
        return list(self._tasks.values())
    
    def update_status(self, task_id: str, status: TaskStatus, result: Any = None, error: str = None):
        if task_id in self._tasks:
            self._tasks[task_id].status = status
            self._tasks[task_id].updated_at = datetime.now()
            if result is not None:
                self._tasks[task_id].result = result
            if error is not None:
                self._tasks[task_id].error = error
