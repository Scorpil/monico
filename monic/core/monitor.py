from typing import Optional
from monic.utils import is_valid_url


class MonitorAttributeError(ValueError):
    pass


class Monitor:
    id: str
    name: str
    endpoint: str
    interval: int

    def __init__(self, id: Optional[str], name: str, endpoint: str, interval: int = 60):
        self.id = id
        self.name = self.preprocess_name(name)
        self.endpoint = self.preprocess_endpoint(endpoint)
        self.interval = self.preprocess_interval(interval)

    @classmethod
    def new(cls, name: str, endpoint: str, interval: Optional[int]):
        return cls(None, name, endpoint, interval)

    @staticmethod
    def preprocess_name(value: str):
        if not value:
            raise MonitorAttributeError("Name cannot be empty")
        if len(value) > 64:
            raise MonitorAttributeError("Name cannot be longer than 64 characters")
        return value

    @staticmethod
    def preprocess_endpoint(value: str):
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
    def preprocess_interval(value: int):
        """Interval must be between 5 and 300 seconds"""
        if value < 5:
            raise MonitorAttributeError("Interval must be at least 5 seconds")
        if value > 300:
            raise MonitorAttributeError("Interval must be at most 300 seconds")
        return value
