import pytest
import time
import os
from monic.storage.pg import PgStorage, StorageSetupException
from monic.core.monitor import Monitor
from monic.core.storage import MonitorAlreadyExistsException, MonitorNotFoundException

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
        cur.execute("SELECT * FROM monic_test_monitors WHERE id = %s", (created_monitor.id,))
        row = cur.fetchone()
        assert row[0] == created_monitor.id
        assert row[1] == created_monitor.name
        assert row[2] == created_monitor.endpoint
        assert row[3] == created_monitor.interval
        assert row[4] == created_monitor.body_regexp
        assert row[5] == created_monitor.last_task_at
        assert row[6] == created_monitor.last_probe_at

    def test_create_monitor_raises_if_already_exists(self):
        monitor = self.storage.create_monitor(Monitor(
            mid=None,
            name="test_monitor_name",
            endpoint="http://example.com",
            interval=60,
            body_regexp="[a-z]+",
        ))
        with pytest.raises(MonitorAlreadyExistsException):
            self.storage.create_monitor(monitor)
    
    def test_list_monitors(self):
        monitor1 = self.storage.create_monitor(Monitor(
            mid=None,
            name="test_monitor_name",
            endpoint="http://example.com",
            interval=60,
            body_regexp="[a-z]+",
        ))
        monitor2 = self.storage.create_monitor(Monitor(
            mid=None,
            name="test_monitor_name",
            endpoint="http://example.com",
            interval=60,
            body_regexp="[a-z]+",
        ))
        assert list(map(lambda m: m.id, self.storage.list_monitors())) == [monitor1.id, monitor2.id]

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
        with pytest.raises(MonitorNotFoundException):
            self.storage.read_monitor(test_monitor.id)