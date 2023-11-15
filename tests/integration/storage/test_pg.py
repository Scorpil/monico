import pytest
import time
import os
from monic.storage.pg import PgStorage, StorageSetupException
from monic.core.monitor import Monitor
from monic.core.storage import MonitorAlreadyExistsException, MonitorNotFoundException
from monic.core.task import Task, TaskStatus
from monic.core.probe import Probe


@pytest.fixture
def test_monitor():
    return Monitor(
        mid="test_id",
        name="test_monitor_name",
        endpoint="http://example.com",
        interval=60,
        body_regexp="[a-z]+",
    )


class TestPgStorage:
    @classmethod
    def setup_class(cls):
        test_postgres_uri = os.environ.get("MONIC_TEST_POSTGRES_URI", None)
        if not test_postgres_uri:
            pytest.skip("Set MONIC_TEST_POSTGRES_URI to enable integration tests")

        cls.storage = PgStorage(test_postgres_uri, prefix="monic_test")
        cls.storage.connect()

    @classmethod
    def teardown_class(cls):
        cls.storage.disconnect()

    def setup_method(self, method):
        self.storage.setup(force=True)

    def teardown_method(self, method):
        self.storage.teardown()

    def test_double_setup(self):
        with pytest.raises(StorageSetupException):
            self.storage.setup()

    def test_create_monitor(self):
        test_monitor = Monitor(
            mid=None,
            name="test_monitor_name",
            endpoint="http://example.com",
            interval=60,
            body_regexp="[a-z]+",
        )
        # verify returned monitor
        created_monitor = self.storage.create_monitor(test_monitor)
        assert isinstance(created_monitor.id, str)
        assert created_monitor.name == test_monitor.name
        assert created_monitor.endpoint == test_monitor.endpoint
        assert created_monitor.interval == test_monitor.interval
        assert created_monitor.body_regexp == test_monitor.body_regexp
        assert created_monitor.last_task_at is None
        assert created_monitor.last_probe_at is None

        # verify monitor in db
        cur = self.storage.conn.cursor()
        cur.execute(
            "SELECT * FROM monic_test_monitors WHERE id = %s", (created_monitor.id,)
        )
        row = cur.fetchone()
        assert row[0] == created_monitor.id
        assert row[1] == created_monitor.name
        assert row[2] == created_monitor.endpoint
        assert row[3] == created_monitor.interval
        assert row[4] == created_monitor.body_regexp
        assert row[5] == created_monitor.last_task_at
        assert row[6] == created_monitor.last_probe_at

    def test_create_monitor_raises_if_already_exists(self):
        monitor = self.storage.create_monitor(
            Monitor(
                mid=None,
                name="test_monitor_name",
                endpoint="http://example.com",
                interval=60,
                body_regexp="[a-z]+",
            )
        )
        with pytest.raises(MonitorAlreadyExistsException):
            self.storage.create_monitor(monitor)

    def test_list_monitors(self):
        monitor1 = self.storage.create_monitor(
            Monitor(
                mid=None,
                name="test_monitor_name",
                endpoint="http://example.com",
                interval=60,
                body_regexp="[a-z]+",
            )
        )
        monitor2 = self.storage.create_monitor(
            Monitor(
                mid=None,
                name="test_monitor_name",
                endpoint="http://example.com",
                interval=60,
                body_regexp="[a-z]+",
            )
        )
        assert list(map(lambda m: m.id, self.storage.list_monitors())) == [
            monitor1.id,
            monitor2.id,
        ]

    def test_read_monitor(self):
        monitor = Monitor(
            mid="test_id",
            name="test_monitor_name",
            endpoint="http://example.com",
            interval=60,
            body_regexp="[a-z]+",
        )
        self.storage.create_monitor(monitor)
        returned_monitor = self.storage.read_monitor(monitor.id)
        assert returned_monitor.id == monitor.id
        assert returned_monitor.name == monitor.name
        assert returned_monitor.endpoint == monitor.endpoint
        assert returned_monitor.interval == monitor.interval
        assert returned_monitor.body_regexp == monitor.body_regexp
        assert returned_monitor.last_task_at is None
        assert returned_monitor.last_probe_at is None

    def test_read_monitor_raises_if_not_found(self):
        with pytest.raises(MonitorNotFoundException):
            self.storage.read_monitor("test_id")

    def test_delete_monitor(self, test_monitor):
        monitor = self.storage.create_monitor(test_monitor)
        self.storage.delete_monitor(test_monitor.id)

    def test_create_task(self, test_monitor):
        monitor = self.storage.create_monitor(test_monitor)
        test_task = monitor.create_task()
        self.storage.create_task(test_task)

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
            "SELECT last_task_at FROM monic_test_monitors WHERE id = %s", (monitor.id,)
        )
        row = cur.fetchone()
        assert row[0] == test_task.timestamp

    def test_lock_tasks(self, test_monitor):
        test_worker = "test_worker"
        test_monitor = self.storage.create_monitor(test_monitor)
        task1 = test_monitor.create_task()
        task1.timestamp = 1700000000
        task2 = test_monitor.create_task()
        task2.timestamp = 1700000001
        task3 = test_monitor.create_task()
        task3.timestamp = 1700000002
        task1 = self.storage.create_task(task1)
        task2 = self.storage.create_task(task2)
        task3 = self.storage.create_task(task3)

        tasks = self.storage.lock_tasks(test_worker, 2)

        # lock_tasks does not guarantee order
        tasks = sorted(tasks, key=lambda t: t.timestamp)

        assert len(tasks) == 2
        assert tasks[0].id == task1.id
        assert tasks[1].id == task2.id

        cur = self.storage.conn.cursor()
        cur.execute(
            "SELECT status, locked_at, locked_by FROM monic_test_tasks WHERE id = %s",
            (task1.id,),
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.RUNNING.value
        assert row[1] is not None
        assert row[2] == test_worker

        cur.execute(
            "SELECT status, locked_at, locked_by FROM monic_test_tasks WHERE id = %s",
            (task2.id,),
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.RUNNING.value
        assert row[1] is not None
        assert row[2] == test_worker

        # task3 should not be locked
        cur.execute(
            "SELECT status, locked_at, locked_by FROM monic_test_tasks WHERE id = %s",
            (task3.id,),
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.PENDING.value
        assert row[1] is None
        assert row[2] is None

    def test_update_task(self, test_monitor):
        self.storage.create_monitor(test_monitor)
        test_task = self.storage.create_task(test_monitor.create_task())

        cur = self.storage.conn.cursor()
        cur.execute(
            "SELECT status FROM monic_test_tasks WHERE id = %s", (test_task.id,)
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.PENDING.value

        test_task.abandon()
        self.storage.update_task(test_task)

        cur.execute(
            "SELECT status FROM monic_test_tasks WHERE id = %s", (test_task.id,)
        )
        row = cur.fetchone()
        assert row[0] == TaskStatus.ABANDONED.value

    def test_record_probe(self, test_monitor):
        self.storage.create_monitor(test_monitor)
        test_task = self.storage.create_task(test_monitor.create_task())
        probe = Probe.create(
            monitor_id=test_monitor.id,
            task_id=test_task.id,
            response_time=0.1,
            response_code=200,
            response_error=None,
            content_match="Hello World",
        )
        self.storage.record_probe(probe)

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

    def test_list_probes(self, test_monitor):
        self.storage.create_monitor(test_monitor)
        test_task = self.storage.create_task(test_monitor.create_task())
        test_probes = []
        for i in range(3):
            test_probes.append(
                Probe.create(
                    monitor_id=test_monitor.id,
                    task_id=test_task.id,
                    response_time=0.1,
                    response_code=200,
                    response_error=None,
                    content_match="Hello World",
                )
            )
            test_probes[-1].timestamp = 1700000000 + i
            self.storage.record_probe(test_probes[-1])

        # list_probes returns two newest probes
        probes = self.storage.list_probes(test_monitor.id, limit=2)
        assert len(probes) == 2
        assert probes[0].id == test_probes[2].id
        assert probes[1].id == test_probes[1].id
