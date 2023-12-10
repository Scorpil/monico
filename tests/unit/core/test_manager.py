import pytest
import asyncio
import time
import logging
from monico.core.manager import Manager
from monico.core.monitor import Monitor
from ..storage import MemStorage


@pytest.fixture
def manager():
    log = logging.getLogger("test")
    log.setLevel(logging.CRITICAL)
    storage = MemStorage()
    storage.monitors = {
        "1": Monitor(
            mid="1",
            name="test monitor",
            endpoint="http://example.com",
            interval=60,
            body_regexp="hello world",
        )
    }
    return Manager(storage, log)


def test_issue_task(manager):
    manager.issue_task(manager.storage.monitors["1"])
    assert len(manager.storage.tasks) == 1
    list(manager.storage.tasks.values())[0].monitor_id == "1"


@pytest.mark.asyncio
async def test_schedule_first_run(manager):
    await manager.schedule()
    assert len(manager.storage.tasks) == 1
    list(manager.storage.tasks.values())[0].monitor_id == "1"


@pytest.mark.asyncio
async def test_schedule_second_run(manager):
    manager.storage.monitors["1"].last_task_at = 1
    await manager.schedule()
    assert len(manager.storage.tasks) == 1
    list(manager.storage.tasks.values())[0].monitor_id == "1"


@pytest.mark.asyncio
async def test_schedule_recent_run(manager):
    # last task was run just now, so no new task should be scheduled
    manager.storage.monitors["1"].last_task_at = int(time.time())
    await manager.schedule()
    assert len(manager.storage.tasks) == 0


@pytest.mark.asyncio
async def test_schedule_run(manager):
    task = asyncio.create_task(manager.run())

    called_once = False
    called_twice = False

    async def fake_schedule():
        nonlocal task, called_once, called_twice
        if not called_once:
            called_once = True
            # raise an exception to verify that the task is not cancelled
            raise Exception("test")
        if not called_twice:
            called_twice = True
            task.cancel()

    manager.schedule = fake_schedule

    await task
    assert called_twice
