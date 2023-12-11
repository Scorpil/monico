"""
Defines an abstract storage class for storing monico data.
"""
from enum import Enum
from abc import ABC, abstractmethod
from monico.core.monitor import Monitor
from monico.core.probe import Probe
from monico.core.task import Task


class StorageConnectionException(Exception):
    """Exception raised when storage connection fails"""

    pass


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


class MonitorSortingOrder(Enum):
    """Defines the sorting order for monitors"""

    CREATED_AT_ASC = "created_at_asc"
    LAST_TASK_AT_DESC = "last_task_at_desc"


class StorageInterface(ABC):
    """Defines the interface for storage backends"""

    def connect(self):
        """Connects to the storage backend. Does nothing by default."""
        pass

    def disconnect(self):
        """Disconnects from the storage backend. Clean up resources. Does nothing by default."""
        pass

    def setup(self):
        """Sets up the storage backend, e.g. creates tables. Does nothing by default."""
        pass

    def teardown(self):
        """Tears down the storage backend, e.g. deletes tables. Does nothing by default."""
        pass

    @abstractmethod
    def create_monitor(self, monitor: Monitor) -> Monitor:
        """Creates a new monitor"""
        raise NotImplementedError

    @abstractmethod
    def list_monitors(
        self, sort: MonitorSortingOrder = MonitorSortingOrder.CREATED_AT_ASC
    ) -> [Monitor]:
        """Lists all monitors"""
        raise NotImplementedError

    @abstractmethod
    def read_monitor(self, id: str) -> Monitor:
        """Gets a monitor by ID"""
        raise NotImplementedError

    @abstractmethod
    def delete_monitor(self, id: str):
        """Deletes a monitor by ID"""
        raise NotImplementedError

    @abstractmethod
    def create_task(self, task: Task):
        """Creates a new task"""
        raise NotImplementedError

    @abstractmethod
    def lock_tasks(self, worker_id: str, batch_size: int) -> [Task]:
        """Locks a batch of tasks."""
        raise NotImplementedError

    @abstractmethod
    def update_task(self, task: Task):
        """Updates a task"""
        raise NotImplementedError

    @abstractmethod
    def record_probe(self, probe):
        """Records the probe"""
        raise NotImplementedError

    @abstractmethod
    def list_probes(self, monitor_id: str, limit: int = 10) -> [Probe]:
        """Lists probes for a monitor"""
        raise NotImplementedError
