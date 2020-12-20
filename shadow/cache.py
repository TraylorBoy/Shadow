"""Cache manager"""

import asyncio
from functools import partial
from typing import Any

from aiocache import Cache
from aiocache.serializers import PickleSerializer


class ShadowCache(object):

    """Cache manager for storing ShadowTasks"""

    # Share state between each instance
    __borg: object = object

    def __init__(self):
        """Instantiates the initial cache instance

        Args:
            cache_type (str, optional): memory, memcached, redis . Defaults to "memory".
        """

        # Uses memory by default
        self.cache: Cache = Cache(serializer=PickleSerializer())

    def init(self):
        """Retrieves shared instance"""

        self.__borg = (
            ShadowCache() if not isinstance(self.__borg, ShadowCache) else self.__borg
        )

        return self.__borg

    def __enter__(self):
        """Allows access to the cache client"""

        return self.init()

    def __exit__(self, *exec_info):
        """Exit context manager"""

        pass

    async def store_task(self, name: str, task: partial):
        """Stores task in cache

        Args:
            name (str): Key to retrieve task from cache
            task (partial): Partial to store in cache
        """

        await self.cache.set(name, task)

    async def get_task(self, name: str):
        """Retrieves task from cache

        Args:
            name (str): Key to retrieve task from cache
        """

        return await self.cache.get(name)

    def store(self, key: str, value: Any):
        """Caches key, value pair in the memcached server

        Args:
            key (str): Key to access the cached value
            value (Any): Value to cache
        """

        asyncio.run(self.store_task(name=key, task=value))

    def retrieve(self, key: str):
        """Retrieves stored key, value pair from the memcached server

        Args:
            key (str): Key for the value to retrieve from cache
        """

        return asyncio.run(self.get_task(name=key))
