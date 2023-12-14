import pytest
from monico.core.monitor import Monitor
from monico.storage.pg import StorageSetupException
from monico.core.probe import Probe
from monico.core.storage import MonitorAlreadyExistsException, MonitorNotFoundException
from .fixtures import test_monitor


class StorageBackendTestSuite:
    @classmethod
    def setup_class(cls):
        cls.storage = cls.build_storage()
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
        self.verify_monitor_created(created_monitor)

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
        self.storage.create_monitor(test_monitor)
        self.storage.read_monitor(test_monitor.id)
        self.storage.delete_monitor(test_monitor.id)

        with pytest.raises(MonitorNotFoundException):
            self.storage.read_monitor(test_monitor.id)

    def test_create_task(self, test_monitor):
        monitor = self.storage.create_monitor(test_monitor)
        test_task = monitor.create_task()
        self.storage.create_task(test_task)

        self.verify_task_created(monitor, test_task)

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
        self.verify_tasks_locked(tasks, test_worker, task1, task2, task3)

    def test_update_task(self, test_monitor):
        self.storage.create_monitor(test_monitor)
        test_task = self.storage.create_task(test_monitor.create_task())
        test_task.abandon()
        self.storage.update_task(test_task)
        self.verify_task_abandoned(test_task)

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
        self.verify_probe_recorded(probe, test_monitor, test_task)

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
