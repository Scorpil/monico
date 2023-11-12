"""
This module contains the main application class.
This class is responsible for managing the whole application execution,
dependency injection, etc.
"""
import asyncio
import logging
from typing import Optional
from monic.core.monitor import Monitor
from monic.core.storage import StorageInterface
from monic.core.manager import Manager
from monic.core.worker import Worker


class App:
    storage: StorageInterface
    log: logging.Logger

    def __init__(self, storage: StorageInterface, log: logging.Logger):
        self.storage = storage
        self.log = log

    def setup(self, force=False):
        """Initializes the application"""
        self.storage.setup(force)

    def create_monitor(
        self, mid: str, name: str, endpoint: str, interval: Optional[int]
    ) -> Monitor:
        """Creates a new monitor"""
        monitor = Monitor(mid, name, endpoint, interval)
        return self.storage.create_monitor(monitor)

    def list_monitors(self) -> [Monitor]:
        """Lists all monitors"""
        return self.storage.list_monitors()

    def delete_monitor(self, mid: str) -> Monitor:
        """Removes a monitor"""
        return self.storage.delete_monitor(mid)

    def run_manager(self):
        """Starts the manager process responsible for scheduling probes"""
        asyncio.run(Manager(self.storage, self.log).run())

    def run_worker(self, worker_id: Optional[str] = None):
        """Starts the worker process responsible for executing probes"""
        asyncio.run(Worker(self.storage, self.log, worker_id).run())

    def shutdown(self):
        """Shuts down the application"""
        self.storage.disconnect()
