import pytest
import os
from monico.storage.pg import PgStorage
from monico.core.monitor import Monitor
from monico.core.task import TaskStatus, Task
from monico.core.probe import Probe
from .storage_backend_test_suite import StorageBackendTestSuite
from .fixtures import test_monitor


class TestPgStorage(StorageBackendTestSuite):
    @classmethod
    def build_storage(cls):
        test_postgres_uri = os.environ.get("MONICO_TEST_POSTGRES_URI", None)
        if not test_postgres_uri:
            pytest.skip("Set MONICO_TEST_POSTGRES_URI to enable integration tests")

        return PgStorage(test_postgres_uri, prefix="monico_test")

    def verify_monitor_created(self, created_monitor):
        cur = self.storage.conn.cursor()
        cur.execute(
            "SELECT * FROM monico_test_monitors WHERE id = %s", (created_monitor.id,)
        )
        row = cur.fetchone()
        assert row[0] == created_monitor.id
        assert row[1] == created_monitor.name
        assert row[2] == created_monitor.endpoint
        assert row[3] == created_monitor.interval
        assert row[4] == created_monitor.body_regexp
        assert row[5] == created_monitor.last_task_at
        assert row[6] == created_monitor.last_probe_at

    def verify_task_created(self, monitor: Monitor, test_task: Task):
        cur = self.storage.conn.cursor()
        cur.execute(
            "SELECT id, timestamp, fk_monitor, status, locked_at, locked_by, completed_at "
            f"FROM {self.storage.tables.tasks} WHERE id = %s",
            (test_task.id,),
        )
        row = cur.fetchone()
        assert row[0] == test_task.id
        assert row[1] == test_task.timestamp
        assert row[2] == monitor.id
        assert row[3] == test_task.status.value
        assert row[4] == test_task.locked_at
        assert row[5] == test_task.locked_by
        assert row[6] == test_task.completed_at

        cur.execute(
            "SELECT last_task_at FROM monico_test_monitors WHERE id = %s", (monitor.id,)
        )
        row = cur.fetchone()
        assert row[0] == test_task.timestamp

    def verify_tasks_locked(
        self,
        tasks: [Task],
        test_worker: str,
        task1_locked: Task,
        task2_locked: Task,
        task3_not_locked: Task,
    ):
        cur = self.storage.conn.cursor()
        cur.execute(
            "SELECT status, locked_at, locked_by FROM monico_test_tasks WHERE id = %s",
            (task1_locked.id,),
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.RUNNING.value
        assert row[1] is not None
        assert row[2] == test_worker

        cur.execute(
            "SELECT status, locked_at, locked_by FROM monico_test_tasks WHERE id = %s",
            (task2_locked.id,),
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.RUNNING.value
        assert row[1] is not None
        assert row[2] == test_worker

        # task3 should not be locked
        cur.execute(
            "SELECT status, locked_at, locked_by FROM monico_test_tasks WHERE id = %s",
            (task3_not_locked.id,),
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.PENDING.value
        assert row[1] is None
        assert row[2] is None

    def verify_task_abandoned(self, test_task: Task):
        cur = self.storage.conn.cursor()

        cur.execute(
            "SELECT status FROM monico_test_tasks WHERE id = %s", (test_task.id,)
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.ABANDONED.value

    def verify_probe_recorded(
        self, probe: Probe, test_monitor: Monitor, test_task: Task
    ):
        cur = self.storage.conn.cursor()
        cur.execute(
            "SELECT id, timestamp, fk_monitor, fk_task, response_time, response_code, response_error, content_match "
            f"FROM {self.storage.tables.probes} WHERE id = %s",
            (probe.id,),
        )
        row = cur.fetchone()
        assert row[0] == probe.id
        assert row[1] == probe.timestamp
        assert row[2] == test_monitor.id
        assert row[3] == test_task.id
        assert row[4] == probe.response_time
        assert row[5] == probe.response_code
        assert row[6] == probe.response_error
        assert row[7] == probe.content_match

        cur.execute(
            f"SELECT last_probe_at FROM {self.storage.tables.monitors} WHERE id = %s",
            (test_monitor.id,),
        )
        row = cur.fetchone()
        assert row[0] == probe.timestamp

        cur.execute(
            f"SELECT status FROM {self.storage.tables.tasks} WHERE id = %s",
            (test_task.id,),
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.COMPLETED.value
