import re
from typing import Optional
from typing import Optional
from monico.utils import is_valid_url
from monico.core.probe import ProbeResponseError, Probe
from monico.core.task import Task


class MonitorAttributeError(ValueError):
    pass


class Monitor:
    id: str
    name: str
    endpoint: str
    interval: int
    body_regexp: Optional[str]
    last_task_at: Optional[int]
    last_probe_at: Optional[int]

    def __init__(
        self,
        mid: Optional[str],
        name: str,
        endpoint: str,
        interval: int = 60,
        body_regexp: Optional[str] = None,
        last_task_at: Optional[int] = None,
        last_probe_at: Optional[int] = None,
    ):
        self.id = self.preprocess_id(mid) if mid else None
        self.name = self.preprocess_name(name)
        self.endpoint = self.preprocess_endpoint(endpoint)
        self.body_regexp = self.preprocess_body_regexp(body_regexp)
        self.interval = self.preprocess_interval(interval)
        self.last_task_at = last_task_at
        self.last_probe_at = last_probe_at

    def create_task(self):
        return Task.create(self.id)

    def __repr__(self):
        return f"<Monitor {self.id} ({self.name})>"

    @staticmethod
    def preprocess_id(value: str) -> str:
        if not re.match(r"^[A-Za-z0-9_-]{1,128}$", value):
            raise MonitorAttributeError(
                f"Monitor ID can only contain alphanumeric characters, underscores and dashes. Got {value}"
            )
        return value

    @staticmethod
    def preprocess_name(value: str) -> str:
        if not value:
            raise MonitorAttributeError("Name cannot be empty")
        if len(value) > 64:
            raise MonitorAttributeError("Name cannot be longer than 64 characters")
        return value

    @staticmethod
    def preprocess_endpoint(value: str) -> str:
        """
        Endpoint must be a valid URL.
        """
        if not value.startswith("http"):
            # we allow omitting the protocol
            # e.g. we'll turn "example.com" into "http://example.com"
            value = f"https://{value}"

        if not is_valid_url(value):
            raise MonitorAttributeError(f'Endpoint must be a valid URL, got "{value}"')

        # we lowercase all URLs
        return value.lower()

    @staticmethod
    def preprocess_interval(value: int) -> int:
        """Interval must be between 5 and 300 seconds"""
        if value < 5:
            raise MonitorAttributeError("Interval must be at least 5 seconds")
        if value > 300:
            raise MonitorAttributeError("Interval must be at most 300 seconds")
        return value

    @staticmethod
    def preprocess_body_regexp(value: Optional[str]) -> str:
        if value is None:
            return value
        try:
            re.compile(value)
        except re.error:
            raise MonitorAttributeError("Invalid body regular expression")
        return value
