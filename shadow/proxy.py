"""Proxy to the given ShadowBot in order to communicate with it while running
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

from loguru import logger

from shadow.bot import ShadowBot


class IShadowProxy(ABC):

    """Proxy Interface"""

    @abstractmethod
    def send(self, bot: ShadowBot, signal: str, block: bool = True):
        pass


class ShadowMediator(IShadowProxy):

    """Connects the proxy to the given ShadowBot"""

    def send(self, shadowbot: ShadowBot, signal: str, block: bool = True):
        """Sends a message to the given ShadowBot

        Args:
            signal (str): Task to perform
            block (bool, optional): Wait for result or not. Defaults to True.
        """

        result: Optional[Any] = None

        shadowbot.messages.put((signal, block))

        return result


class ShadowProxy(IShadowProxy):

    """Communicates with running ShadowBot"""

    def __init__(self, bot: ShadowBot):
        """Creates a proxy for the given ShadowBot

        Args:
            bot (ShadowBot): ShadowBot to establish a connection with
        """

        self.__mediator = ShadowMediator()
        self.__bot = bot

    def send(self, shadowbot: ShadowBot, signal: str, block: bool = True):
        """Sends a message to the given ShadowBot

        Args:
            signal (str): Task to perform
            block (bool, optional): Wait for result or not. Defaults to True.
        """

        if not self.__bot.running():
            logger.error("ShadowBot is not running")
            return None

        self.__mediator.send(shadowbot=self.__bot, signal=signal, block=block)
