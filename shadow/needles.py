"""ShadowBot Manager"""

import os
import dill

from copy import copy

from shadow.bot import ShadowBot
from functools import partial

from typing import Dict, List

from loguru import logger


class Needles(object):

    """Manages ShadowBots on the ShadowNetwork"""

    def __repr__(self):
        """
        Needles: {self.count()}
        -----------------------
        {bot_info}
        """

        bot_info: str = ""

        for _, bot in self.needles.items():
            bot_info += str(bot)

        _needle_str: str = f"""
        Needles: {self.count()}
        -----------------------
        {bot_info}
        """

        return _needle_str

    def __init__(self):
        """Sets initial needles state"""

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

        if not self.check(name=bot.id):
            self.needles[bot.id] = bot

            logger.debug(f"{bot.id} sewn")

            # Cache the needles dictionary
            self.save() if save else None

    def retract(self, bot: ShadowBot):
        """Unregisters ShadowBot from the needles dictionary

        Args:
            bot (ShadowBot): Instantiated ShadowBot instance

        Returns:
            [Dict[str, Dict[str, partial]]]: The ShadowBots name and tasks used to initialize the instance
        """

        essence: Dict[str, Dict[str, partial]] = {}

        if self.check(name=bot.id):

            # Remove the needle from the needles dictionary
            essence = self.needle(bot)
            del self.needles[bot.id]

            logger.debug(f"{essence} retracted")

            # Cache the needles dictionary
            self.save()

        return essence

    def can_load(self):
        """Checks if cache file exists

        Returns:
            [bool]: Cache file exists
        """

        return os.path.exists(self.__path)

    def load(self):
        """Loads the needles dictionary from cache"""

        logger.debug(f"Loading Needles from cache")

        with open(self.__path, "rb") as cache_file:

            _needles: Dict[str, Dict[str, partial]] = copy(dill.load(cache_file))

            # Build ShadowBots and register them
            for _id, tasks in _needles.items():
                self.sew(bot=ShadowBot(name=_id, tasks=tasks), save=False)

        logger.debug(f"Needles loaded: {self.needles}")

    def save(self):
        """Stores needles dictionary in cache"""

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
        """Removes cache file at __path"""

        os.remove(self.__path) if os.path.exists(self.__path) else None

    def check(self, name: str):
        """Checks if ShadowBot is registered

        Args:
            bot (ShadowBot): Instantiated ShadowBot instance

        Returns:
            [bool]: ShadowBot is registered or not
        """

        return name in self.needles.keys()

    def count(self):
        """Count the number of sewn ShadowBot instances

        Returns:
            [int]: Length of needles
        """

        return len(self.needles)

    def needle(self, bot: ShadowBot):
        """Retrieves ShadowBot init params from instantiated instance

        Args:
            bot (ShadowBot): Instantiated ShadowBot instance

        Returns:
            [Dict[str, Dict[str, partial]]]: ShadowBots name and tasks used to initialize the instance
        """

        needle: Dict[str, Dict[str, partial]] = {}
        needle[bot.id] = {}

        # Retrieve partial from clone
        for task, clone in bot.clones.items():
            needle[bot.id][task] = clone.task

        return needle

    def get(self, name: str):
        """Retrieves ShadowBot from needles dictionary

        Args:
            name (str): ShadowBot to retrieve
        """

        if name in self.needles.keys():
            return self.needles[name]
