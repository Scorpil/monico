import re
import time
import asyncio
import logging
import uuid
import aiohttp
from monico.core.storage import StorageInterface
from monico.core.task import Task
from monico.core.probe import Probe, ProbeResponseError
from typing import Optional


class Worker:
    """Worker process responsible for executing probes"""

    MIN_WAIT_TIME = 5  # seconds to wait between locking batches
    REQUEST_TIMEOUT = 5  # seconds until a request is considered timed out
    STALE_THRESHOLD = 600  # seconds until a task is considered stale
    BATCH_SIZE = 10  # number of tasks to lock at once

    worker_id: str
    storage: StorageInterface
    log: logging.Logger

    def __init__(
        self,
        storage: StorageInterface,
        log: logging.Logger,
        worker_id: Optional[str] = None,
    ):
        self.worker_id = worker_id or str(uuid.uuid4())
        self.storage = storage
        self.log = log

    def lock_batch(self):
        """Locks a batch of tasks"""
        return self.storage.lock_tasks(self.worker_id, batch_size=self.BATCH_SIZE)

    async def run(self):
        """Starts the worker process"""
        self.log.info(f"worker has started; id={self.worker_id}")

        while True:
            self.log.debug(
                f"worker is locking a batch of tasks; batch_size={self.BATCH_SIZE}"
            )
            try:
                batch = self.lock_batch()
            except Exception as e:
                self.log.error(
                    f"worker encountered an unexpected exception while locking: {e}"
                )
                await asyncio.sleep(self.MIN_WAIT_TIME)
                continue
            self.log.debug(f"worker has locked a {len(batch)} tasks")

            tasks = [self.run_task(task) for task in batch]
            try:
                # wait minimum of 5 seconds before locking another batch
                await asyncio.gather(asyncio.sleep(self.MIN_WAIT_TIME), *tasks)
            except Exception as e:
                self.log.error(f"worker encountered an unexpected exception: {e}")
                continue
            except asyncio.CancelledError:
                self.log.info("worker process has been cancelled")
                break

    async def run_task(self, task: Task):
        """Runs a single instance of a task (probe) and records the result"""
        now = int(time.time())
        self.log.debug(f"worker is running a task; task_id={task.id}")

        # tasks that are too old are stale and should be abandoned
        if now - task.timestamp > self.STALE_THRESHOLD:
            self.log.warning(f"abandoning a stale task; task_id={task.id}")
            task.abandon()
            self.storage.update_task(task)
            return

        # record the probe
        probe = await self.get_probe(task)
        self.storage.record_probe(probe)
        self.log.debug(
            f"worker has recorded a probe; task_id={probe.task_id} probe_id={probe.id}"
        )

    async def get_probe(self, task: Task) -> Probe:
        """Executes an http request and returns a probe based on the response"""
        self.log.debug(f"worker is executing a probe; task_id={task.id}")
        monitor = self.storage.read_monitor(task.monitor_id)

        start = asyncio.get_event_loop().time()
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT)
        ) as session:
            try:
                async with session.get(monitor.endpoint) as response:
                    request_time = asyncio.get_event_loop().time() - start
                    response_text = await response.text()

                    match_str = None
                    if monitor.body_regexp:
                        match = re.search(monitor.body_regexp, response_text)
                        match_str = match.group(0) if match else None
                    return Probe.create(
                        monitor_id=task.monitor_id,
                        task_id=task.id,
                        response_time=request_time,
                        response_code=response.status,
                        response_error=None,
                        content_match=match_str,
                    )
            except aiohttp.ClientError as e:
                request_time = asyncio.get_event_loop().time() - start
                return Probe.create(
                    monitor_id=task.monitor_id,
                    task_id=task.id,
                    response_time=request_time,
                    response_code=None,
                    response_error=ProbeResponseError.CONNECTION_ERROR,
                    content_match=None,
                )
            except asyncio.TimeoutError:
                request_time = asyncio.get_event_loop().time() - start
                return Probe.create(
                    monitor_id=task.monitor_id,
                    task_id=task.id,
                    response_time=request_time,
                    response_code=None,
                    response_error=ProbeResponseError.TIMEOUT,
                    content_match=None,
                )
