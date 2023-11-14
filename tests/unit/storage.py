import uuid
from monic.core.storage import StorageInterface
from monic.core.monitor import Monitor
from monic.core.task import TaskStatus, Task


class MemStorage(StorageInterface):
    """
    Memory storage implementation for monic.
    Used for testing to avoid database dependencies.
    """

    def __init__(self):
        self.monitors = {}
        self.tasks = {}
        self.probes = {}

    def create_monitor(self, monitor):
        id = uuid.uuid4().hex
        self.monitors[monitor.id] = monitor
        return Monitor(
            id, monitor.name, monitor.endpoint, monitor.interval, monitor.body_regexp
        )

    def list_monitors(self, sort=None):
        return list(self.monitors.values())

    def read_monitor(self, id):
        return self.monitors[id]

    def delete_monitor(self, id):
        del self.monitors[id]

    def create_task(self, task):
        self.tasks[task.id] = task
        self.monitors[task.monitor_id].last_task_at = task.timestamp

    def lock_tasks(self, worker_id, batch_size):
        locked = []
        selected = [
            task for task in self.tasks.values() if task.status == TaskStatus.PENDING
        ][:batch_size]
        for task in selected:
            task.status = TaskStatus.RUNNING
            task.worker_id = worker_id
            locked.append(task)
        return locked

    def update_task(self, task):
        self.tasks[task.id] = task

    def record_probe(self, probe):
        self.probes[probe.id] = probe
        self.tasks[probe.task_id].status = TaskStatus.COMPLETED
        self.monitors[
            self.tasks[probe.task_id].monitor_id
        ].last_probe_at = probe.timestamp

    def list_probes(self, monitor_id: str, limit: int = 10):
        return [
            probe for probe in self.probes.values() if probe.monitor_id == monitor_id
        ]
