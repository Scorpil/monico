"""
Defines an abstract storage class for storing monic data.
"""
from abc import ABC, abstractmethod
from monic.core.monitor import Monitor


class StorageInterface(ABC):
    @abstractmethod
    def create_monitor(self, monitor: Monitor) -> Monitor:
        """Creates a new monitor"""
        raise NotImplementedError

    @abstractmethod
    def list_monitors(self) -> [Monitor]:
        """Lists all monitors"""
        raise NotImplementedError

    @abstractmethod
    def read_monitor(self, id: str) -> Monitor:
        """Gets a monitor by ID"""
        raise NotImplementedError

    @abstractmethod
    def update_monitor(self, monitor: Monitor) -> Monitor:
        """Updates a monitor"""
        raise NotImplementedError

    @abstractmethod
    def delete_monitor(self, id: str):
        """Deletes a monitor by ID"""
        raise NotImplementedError
