import time
import asyncio
import logging
from monico.core.storage import StorageInterface, MonitorSortingOrder
from monico.core.monitor import Monitor


class Manager:
    MIN_WAIT_TIME = 5  # seconds to wait between scheduling tasks

    storage: StorageInterface
    log: logging.Logger

    def __init__(self, storage: StorageInterface, log: logging.Logger):
        self.storage = storage
        self.log = log

    def issue_task(self, monitor: Monitor):
        self.log.debug(f"issuing task for monitor {monitor.id}")
        self.storage.create_task(monitor.create_task())

    async def schedule(self):
        """
        Loops over all monitors and schedules a task if necessary.
        """
        now = int(time.time())
        monitors = self.storage.list_monitors(
            sort=MonitorSortingOrder.LAST_TASK_AT_DESC
        )
        self.log.debug(f"scheduling: found {len(monitors)} monitors")

        for monitor in monitors:
            if monitor.last_task_at is None:
                self.log.debug(f"monitor {monitor.id} has never run: scheduling.")
                self.issue_task(monitor)
                continue

            seconds_since_last_task = now - monitor.last_task_at
            if seconds_since_last_task >= monitor.interval:
                self.log.debug(
                    f"Monitor {monitor.id} has not been issuing a task for "
                    f"{seconds_since_last_task} seconds, which is longer or "
                    f"equal to the the interval of {monitor.interval} seconds:"
                    " scheduling."
                )
                self.issue_task(monitor)
                continue

            self.log.debug(
                f"Monitor {monitor.id} has not been issuing a task for "
                f"{seconds_since_last_task} seconds, which is less than the "
                f"interval of {monitor.interval} seconds: skipping."
            )

    async def run(self):
        self.log.info(f"manager has started")

        while True:
            try:
                await asyncio.gather(
                    asyncio.sleep(self.MIN_WAIT_TIME),
                    self.schedule(),
                )
            except Exception as e:
                self.log.error(f"manager encountered an unexpected exception: {e}")
            except asyncio.CancelledError:
                self.log.info("manager process has been cancelled")
                break
