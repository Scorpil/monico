import asyncio
from monic.core.storage import StorageInterface


class Manager:
    storage: StorageInterface

    def __init__(self, storage: StorageInterface):
        self.storage = storage

    async def run(self):
        while True:
            await asyncio.sleep(1)
