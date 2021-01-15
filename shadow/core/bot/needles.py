"""ShadowBot Manager"""

import os
import dill

from copy import copy

from typing import Dict, Any

from loguru import logger

from .bot import ShadowBot
from .needle import Needle
from shadow.core.helpers import Borg

from typing import List, Any

class Needles(Borg):

    """Manages ShadowBots on the ShadowNetwork"""

    def __init__(self):
        """Sets initial needles state"""

        self.__setup()
        self.__path: str = os.path.join("shadow/data/cache/", self.cache_file)

    def __setup(self): # pragma: no cover
        """Setup singleton instance
        """

        super().__init__()

        ATTR: List[str] = ["pool", "cache_file"]

        setters: Dict[str, Any] = {
            "pool": {},
            "cache_file": "needles.cache"
        }

        for attribute in ATTR:
            if not hasattr(self, attribute):
                setattr(self, attribute, setters[attribute])

    # ---------------------------------- Context --------------------------------- #

    def __enter__(self):
        """Context manager method
        """

        # Load the pool from cache
        if self.can_load():
            self.load()

    def __exit__(self, *exec_info):
        """Cleanup the context manager
        """

        # Store the pool in cache
        self.save()

    def __del__(self):
        """Cleanup the instance
        """

        # Store the pool in cache
        self.save()

    # ----------------------------------- Core ----------------------------------- #

    def can_load(self):
        """Checks if cache file exists

        Returns:
            [bool]: Cache file exists
        """

        return os.path.exists(self.__path)

    def load(self):
        """Loads the needle pool from cache"""

        with open(self.__path, "rb") as cache_file:
            self.pool = copy(dill.load(cache_file))

        logger.debug(f"Needles loaded: {self.pool}")

    def save(self):
        """Stores pool in cache"""

        logger.debug(f"Storing Needles in cache")

        with open(self.__path, "wb") as cache_file:
            dill.dump(self.pool, cache_file)

        logger.debug(f"Needles stored")

    def reset(self):
        """Removes cache file at __path"""

        os.remove(self.__path) if os.path.exists(self.__path) else None

    def sew(self, essence: Needle):
        """Registers a ShadowBot on the network

        Args:
            essence (Needle): The ShadowBot's properties
        """

        name, _, _ = essence

        if not self.check(name):
            self.pool[name] = essence

            logger.debug(f"Registered: {name}")

    def retract(self, name: str):
        """Removes a ShadowBot from the network

        Args:
            name (str): Name of the ShadowBot to be removed
        """

        if self.check(name):
            del self.pool[name]

            logger.debug(f"Unregistered: {name}")

    def check(self, name: str):
        """Checks if a ShadowBot is registered

        Args:
            name (str): Name of ShadowBot to be checked

        Returns:
            [bool]: ShadowBot is registered or not
        """

        return name in self.pool.keys()

    def get(self, name: str):
        """Retrieves a ShadowBot from the pool

        Args:
            name (str): Name of the ShadowBot to be retrieved

        Returns:
            [ShadowBot]: Instatiated ShadowBot instance
        """

        if self.check(name):
            # Create the ShadowBot from it's essence
            essence: Needle = self.pool[name]
            name, tasks, history = essence
            shadowbot: ShadowBot = ShadowBot(name, tasks, history)

            return shadowbot
