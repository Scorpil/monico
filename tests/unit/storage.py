import uuid
from monic.core.storage import StorageInterface
from monic.core.monitor import Monitor


class MemStorage(StorageInterface):
    """
    Memory storage implementation for monic.
    Used for testing to avoid database dependencies.
    """

    def __init__(self):
        self.monitors = {}

    def create_monitor(self, monitor):
        id = uuid.uuid4().hex
        self.monitors[monitor.id] = monitor
        return Monitor(
            id, monitor.name, monitor.endpoint, monitor.interval, monitor.body_regexp
        )

    def list_monitors(self):
        return list(self.monitors.values())

    def read_monitor(self, id):
        return self.monitors[id]

    def delete_monitor(self, id):
        del self.monitors[id]
