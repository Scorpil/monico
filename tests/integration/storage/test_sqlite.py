import pytest
import shutil
import tempfile
from monico.storage.sqlite import SqliteStorage
from monico.core.monitor import Monitor
from monico.core.task import Task, TaskStatus
from monico.core.probe import Probe
from .storage_backend_test_suite import StorageBackendTestSuite
from .fixtures import test_monitor


class TestSqliteStorage(StorageBackendTestSuite):
    @classmethod
    def build_storage(cls):
        cls.tmpdir = tempfile.mkdtemp()
        test_sqlite_uri = f"{cls.tmpdir}/monico_test.db"
        return SqliteStorage(test_sqlite_uri, prefix="monico_test")

    @classmethod
    def teardown_class(cls):
        super().teardown_class()
        shutil.rmtree(cls.tmpdir)

    def test_connect_error(self):
        storage = SqliteStorage("file:///nonexistent.db")
        with pytest.raises(Exception):
            storage.connect()

    def verify_monitor_created(self, created_monitor):
        cur = self.storage.conn.cursor()
        cur.execute(
            f"SELECT * FROM {self.storage.tables.monitors} WHERE id = :id",
            {"id": created_monitor.id},
        )
        row = cur.fetchone()
        assert row[0] == created_monitor.id
        assert row[1] == created_monitor.name
        assert row[2] == created_monitor.endpoint
        assert row[3] == created_monitor.interval
        assert row[4] == created_monitor.body_regexp
        assert row[5] == created_monitor.last_task_at
        assert row[6] == created_monitor.last_probe_at

    def verify_task_created(self, monitor, test_task):
        cur = self.storage.conn.cursor()
        cur.execute(
            "SELECT "
            "id, timestamp, fk_monitor, status, "
            "locked_at, locked_by, completed_at "
            f"FROM {self.storage.tables.tasks} WHERE id = :id",
            {"id": test_task.id},
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
            f"SELECT last_task_at FROM {self.storage.tables.monitors} WHERE id = :id",
            {"id": monitor.id},
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
        assert len(tasks) == 2
        assert tasks[0].id == task1_locked.id
        assert tasks[1].id == task2_locked.id

        cur = self.storage.conn.cursor()
        cur.execute(
            "SELECT status, locked_at, locked_by FROM monico_test_tasks WHERE id = :id",
            (task1_locked.id,),
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.RUNNING.value
        assert row[1] is not None
        assert row[2] == test_worker

        cur.execute(
            "SELECT status, locked_at, locked_by FROM monico_test_tasks WHERE id = :id",
            (task2_locked.id,),
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.RUNNING.value
        assert row[1] is not None
        assert row[2] == test_worker

        # task3 should not be locked
        cur.execute(
            "SELECT status, locked_at, locked_by FROM monico_test_tasks WHERE id = :id",
            (task3_not_locked.id,),
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.PENDING.value
        assert row[1] is None
        assert row[2] is None

    def verify_task_abandoned(self, test_task: Task):
        cur = self.storage.conn.cursor()
        cur.execute(
            "SELECT status FROM monico_test_tasks WHERE id = :id", {"id": test_task.id}
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.ABANDONED.value

    def verify_probe_recorded(
        self, probe: Probe, test_monitor: Monitor, test_task: Task
    ):
        cur = self.storage.conn.cursor()
        cur.execute(
            "SELECT id, timestamp, fk_monitor, fk_task, "
            "response_time, response_code, response_error, content_match "
            f"FROM {self.storage.tables.probes} WHERE id = :id",
            {"id": probe.id},
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
            f"SELECT last_probe_at FROM {self.storage.tables.monitors} WHERE id = :id",
            {"id": test_monitor.id},
        )
        row = cur.fetchone()
        assert row[0] == probe.timestamp

        cur.execute(
            f"SELECT status FROM {self.storage.tables.tasks} WHERE id = :id",
            {"id": test_task.id},
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.COMPLETED.value
