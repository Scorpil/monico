"""
This module contains the main application class.
This class is responsible for managing the whole application execution,
dependency injection, etc.
"""
from typing import Optional
from monic.core.monitor import Monitor
from monic.core.storage import StorageInterface


class App:
    storage: StorageInterface

    def __init__(self, storage: StorageInterface):
        self.storage = storage

    def setup(self, force=False):
        """Initializes the application"""
        self.storage.setup(force)

    def add_monitor(
        self, mid: str, name: str, endpoint: str, interval: Optional[int]
    ) -> Monitor:
        """Creates a new monitor"""
        monitor = Monitor(mid, name, endpoint, interval)
        return self.storage.create_monitor(monitor)
