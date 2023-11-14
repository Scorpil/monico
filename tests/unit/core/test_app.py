import pytest
import logging
from unittest import mock
from monic.core.app import App
from monic.core.monitor import Monitor
from monic.core.probe import Probe
from monic.core.worker import Worker
from monic.core.manager import Manager
from ..storage import MemStorage


@pytest.fixture
def app():
    log = logging.getLogger("test")
    log.setLevel(logging.CRITICAL)
    storage = MemStorage()
    return App(storage, log)


def test_setup(app):
    setup_called = False
    setup_called_with_force = False

    def fake_setup(force=False):
        nonlocal setup_called, setup_called_with_force
        setup_called = True
        setup_called_with_force = force

    app.storage.setup = fake_setup

    # test setup with force
    app.setup(force=True)
    assert setup_called
    assert setup_called_with_force

    # test setup without force (default)
    setup_called = False
    app.setup()
    assert setup_called
    assert not setup_called_with_force


def test_status(app):
    app.storage.monitors = {
        "1": Monitor(
            mid="1",
            name="test monitor",
            endpoint="http://example.com",
            interval=60,
            body_regexp="hello world",
        )
    }
    app.storage.probes = {
        "1": Probe(
            id="probe_id",
            timestamp=1,
            monitor_id="1",
            task_id="task_id",
            response_code=200,
            response_time=0.1,
            response_error=None,
            content_match="hello world",
        )
    }
    monitor, probes = app.status("1")
    assert monitor.id == "1"
    assert len(probes) == 1
    assert probes[0].id == "probe_id"


def test_create_monitor(app):
    app.create_monitor(
        mid="1",
        name="test monitor",
        endpoint="http://example.com",
        interval=60,
        body_regexp="hello world",
    )
    assert len(app.storage.monitors) == 1
    assert list(app.storage.monitors.values())[0].id == "1"


def test_list_monitors(app):
    app.storage.monitors = {
        "1": Monitor(
            mid="1",
            name="test monitor",
            endpoint="http://example.com",
            interval=60,
            body_regexp="hello world",
        )
    }
    monitors = app.list_monitors()
    assert len(monitors) == 1
    assert monitors[0].id == "1"


def test_delete_monitor(app):
    app.storage.monitors = {
        "1": Monitor(
            mid="1",
            name="test monitor",
            endpoint="http://example.com",
            interval=60,
            body_regexp="hello world",
        )
    }
    app.delete_monitor("1")
    assert len(app.storage.monitors) == 0


def test_run_manager(app):
    with mock.patch.object(Manager, "run") as mock_run:
        app.run_manager()
        mock_run.assert_called_once()


def test_run_worker(app):
    with mock.patch.object(Worker, "run") as mock_run:
        app.run_worker()
        mock_run.assert_called_once()


def test_shutdown(app):
    disconnect_called = False

    def fake_disconnect():
        nonlocal disconnect_called
        disconnect_called = True

    app.storage.disconnect = fake_disconnect
    app.shutdown()
    assert disconnect_called
