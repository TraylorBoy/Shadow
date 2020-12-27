"""ShadowBot Manager"""

import os
import dill

from copy import copy

from shadow.bot import ShadowBot
from functools import partial

from typing import Dict

from loguru import logger

class Needles(object):

    """Manages ShadowBots on the ShadowNetwork"""


    def __init__(self):
        """Sets initial needles state
        """

        self.needles: Dict[str, ShadowBot] = {}
        self.__cache_file: str = "needles.cache"
        self.__path: str = os.path.join("shadow/data/cache/", self.__cache_file)

        # Load the needles dictionary from cache
        if self.can_load():
            self.load()

    def sew(self, bot: ShadowBot, save: bool = True):
        """Adds a ShadowBot to the needles dictionary

        Args:
            bot (ShadowBot): Instantiated ShadowBot instance
            save (bool): Whether to save the needles dictionary in cache or not
        """

        if bot.id not in self.needles.keys():
            self.needles[bot.id] = bot

            logger.debug(f"{bot.id} sewn")

            # Cache the needles dictionary
            self.save() if save else None

    def retract(self, bot: ShadowBot):
        """Unregisters ShadowBot from the needles dictionary

        Args:
            bot (ShadowBot): Instantiated ShadowBot instance
        """

        if bot.id in self.needles.keys():
            del self.needles[bot.id]

            logger.debug(f"{bot.id} retracted")

            # Cache the needles dictionary
            self.save()

    def can_load(self):
        """Checks if cache file exists

        Returns:
            [bool]: Cache file exists
        """

        return os.path.exists(self.__path)

    def load(self):
        """Loads the needles dictionary from cache
        """

        logger.debug(f"Loading Needles from cache")

        with open(self.__path, "rb") as cache_file:

            _needles: Dict[str, Dict[str, partial]] = copy(dill.load(cache_file))

            # Build ShadowBots and register them
            for _id, tasks in _needles.items():
                self.sew(bot=ShadowBot(name=_id, tasks=tasks), save=False)

        logger.debug(f"Needles loaded: {self.needles}")

    def save(self):
        """Stores needles dictionary in cache
        """

        logger.debug(f"Storing Needles in cache")

        with open(self.__path, "wb") as cache_file:
            _needles: Dict[str, Dict[str, partial]] = {}

            # Store clones instead
            for _id, bot in self.needles.items():
                _needles[_id] = {}

                # Retrieve partial from clone
                for task, clone in bot.clones.items():
                    _needles[_id][task] = clone.task

            dill.dump(_needles, cache_file)

        logger.debug(f"Needles stored")

    def reset(self):
        """Removes cache file at __path
        """

        os.remove(self.__path)

    def check(self, bot: ShadowBot):
        """Checks if ShadowBot is registered

        Args:
            bot (ShadowBot): Instantiated ShadowBot instance

        Returns:
            [bool]: ShadowBot is registered or not
        """

        return bot.id in self.needles.keys()


