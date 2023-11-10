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

    def add_monitor(self, name: str, endpoint: str, interval: Optional[int]) -> Monitor:
        """Creates a new monitor"""
        monitor = Monitor.new(name, endpoint, interval)
        return self.storage.create_monitor(monitor)
