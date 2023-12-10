import pytest
import time
import logging
import asyncio
import aiohttp
from aioresponses import aioresponses
from monico.core.worker import Worker
from monico.core.monitor import Monitor
from monico.core.task import Task, TaskStatus
from monico.core.probe import Probe, ProbeResponseError
from ..storage import MemStorage


@pytest.fixture
def worker():
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
    return Worker(storage, log)


def test_lock_batch(worker: Worker):
    task1 = Task.create(1)
    task2 = Task.create(1)
    worker.storage.tasks = {
        "1": task1,
        "2": task2,
    }

    tasks = worker.lock_batch()
    assert len(tasks) == 2
    assert tasks[0].id == task1.id
    assert tasks[1].id == task2.id


@pytest.mark.asyncio
async def test_run(worker):
    TIMEOUT = 5  # seconds until test times out

    # sent 3 batches of tasks, each batch has 1 task
    total_tasks = 3
    sent_tasks = 0

    def fake_lock_batch():
        # on first three calls, return a task.
        # on the fourth call and later, return an empty list.
        nonlocal sent_tasks
        sent_tasks += 1
        if sent_tasks > total_tasks:
            return []
        return [worker.storage.monitors["1"].create_task()]

    worker.lock_batch = fake_lock_batch

    # record the number of tasks completed
    tasks_completed = 0

    def fake_run_task(task):
        nonlocal tasks_completed
        tasks_completed += 1
        return task

    worker.run_task = fake_run_task

    worker_task = asyncio.create_task(worker.run())

    async def test_all_task_completed():
        start = time.time()
        while True:
            if tasks_completed == total_tasks:
                return worker_task.cancel()
            await asyncio.sleep(0.1)
            if (time.time() - start) > TIMEOUT:
                raise Exception("test timed out")

    await asyncio.gather(worker_task, test_all_task_completed(), return_exceptions=True)
    assert tasks_completed == total_tasks


@pytest.mark.asyncio
async def test_run_task_stale(worker: Worker):
    task = Task.create(1)

    # make the task stale
    task.timestamp = int(time.time()) - Worker.STALE_THRESHOLD - 1
    worker.storage.tasks = {
        task.id: task,
    }

    await worker.run_task(task)
    assert worker.storage.tasks[task.id].status == TaskStatus.ABANDONED


@pytest.mark.asyncio
async def test_run_task_success(worker: Worker):
    test_probe_content_match = "hello world"

    async def fake_get_probe(task: Task):
        return Probe.create(
            monitor_id=task.monitor_id,
            task_id=task.id,
            response_time=0.1,
            response_code=200,
            response_error=None,
            content_match=test_probe_content_match,
        )

    worker.get_probe = fake_get_probe
    task = worker.storage.monitors["1"].create_task()
    worker.storage.tasks = {
        task.id: task,
    }

    await worker.run_task(task)
    assert len(worker.storage.probes) == 1
    stored_probe = list(worker.storage.probes.values())[0]
    assert stored_probe.content_match == test_probe_content_match


@pytest.mark.asyncio
async def test_get_probe_success(worker: Worker):
    monitor = worker.storage.monitors["1"]
    task = worker.storage.monitors["1"].create_task()

    with aioresponses() as mocked:
        mocked.get(monitor.endpoint, status=200, body="*** hello world ***")
        probe = await worker.get_probe(task)

    assert probe.monitor_id == monitor.id
    assert probe.task_id == task.id
    assert probe.response_code == 200
    assert probe.response_error == None
    assert probe.content_match == "hello world"


@pytest.mark.asyncio
async def test_get_probe_connection_error(worker: Worker):
    monitor = worker.storage.monitors["1"]
    task = worker.storage.monitors["1"].create_task()

    with aioresponses() as mocked:
        mocked.get(monitor.endpoint, exception=aiohttp.ClientError)
        probe = await worker.get_probe(task)

    assert probe.monitor_id == monitor.id
    assert probe.task_id == task.id
    assert probe.response_code == None
    assert probe.response_error == ProbeResponseError.CONNECTION_ERROR
    assert probe.content_match == None


@pytest.mark.asyncio
async def test_get_probe_timeout_error(worker: Worker):
    monitor = worker.storage.monitors["1"]
    task = worker.storage.monitors["1"].create_task()

    with aioresponses() as mocked:
        mocked.get(monitor.endpoint, exception=asyncio.TimeoutError)
        probe = await worker.get_probe(task)

    assert probe.monitor_id == monitor.id
    assert probe.task_id == task.id
    assert probe.response_code == None
    assert probe.response_error == ProbeResponseError.TIMEOUT
    assert probe.content_match == None
