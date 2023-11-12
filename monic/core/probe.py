from enum import Enum
from typing import Optional
import time
import uuid


class ProbeResponseError(Enum):
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"


class Probe:
    id: str
    timestamp: int
    monitor_id: str
    task_id: str
    response_time: float
    response_code: int
    response_error: str
    content_match: str

    def __init__(
        self,
        monitor_id: str,
        task_id: str,
        response_time: Optional[float],
        response_code: Optional[int],
        response_error: Optional[ProbeResponseError],
        content_match: Optional[str],
    ):
        self.id = str(uuid.uuid4())
        self.monitor_id = monitor_id
        self.task_id = task_id
        self.timestamp = int(time.time())
        self.response_time = response_time
        self.response_code = response_code
        self.response_error = response_error
        self.content_match = content_match
