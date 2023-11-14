import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    FAILED = "failed"


@dataclass
class Task:
    id: str
    timestamp: int
    monitor_id: str
    status: TaskStatus
    locked_at: Optional[int] = None
    locked_by: Optional[str] = None
    completed_at: Optional[int] = None

    @classmethod
    def create(cls, monitor_id: str):
        """
        Creates a new task for the given monitor ID.
        """
        return cls(
            id=str(uuid.uuid4()),
            timestamp=int(time.time()),
            monitor_id=monitor_id,
            status=TaskStatus.PENDING,
        )

    def abandon(self):
        """
        Abandons the task.
        """
        self.status = TaskStatus.ABANDONED
