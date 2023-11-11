"""
Defines an abstract storage class for storing monic data.
"""
from abc import ABC, abstractmethod
from monic.core.monitor import Monitor


class StorageSetupException(Exception):
    """Exception raised when storage setup fails"""

    pass


class MonitorAlreadyExistsException(Exception):
    """Exception raised when creating a monitor that already exists"""

    # TODO: handle situations where the monitor already exists
    pass


class MonitorNotFoundException(Exception):
    """Exception raised when a monitor is not found"""

    pass


class StorageInterface(ABC):
    def connect(self):
        """Connects to the storage backend"""
        pass

    def setup(self):
        """Sets up the storage backend, e.g. creates tables"""
        pass

    def teardown(self):
        """Tears down the storage backend, e.g. deletes tables"""
        pass

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
