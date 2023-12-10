from dataclasses import dataclass
from enum import Enum
from typing import Optional
import time
import uuid


class ProbeResponseError(Enum):
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"


@dataclass
class Probe:
    id: str
    timestamp: int
    monitor_id: str
    task_id: str
    response_time: float
    response_code: int
    response_error: str
    content_match: str

    @staticmethod
    def create(
        monitor_id: str,
        task_id: str,
        response_time: Optional[float],
        response_code: Optional[int],
        response_error: Optional[ProbeResponseError],
        content_match: Optional[str],
    ):
        return Probe(
            id=str(uuid.uuid4()),
            monitor_id=monitor_id,
            task_id=task_id,
            timestamp=int(time.time()),
            response_time=response_time,
            response_code=response_code,
            response_error=response_error,
            content_match=content_match,
        )
