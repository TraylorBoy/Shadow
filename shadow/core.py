"""Facade for interacting with the application"""

from datetime import datetime
from typing import Optional

from loguru import logger

from shadow.bot import ShadowBot
from shadow.observer import ShadowObserver

# Setup log file
logger.add(
    f"shadow/logs/{datetime.now().month}_{datetime.now().day}_{datetime.now().year}.log",
    rotation="500 MB",
    enqueue=True,
)


class Shadow:

    """Entry point"""

    def build(self, name: Optional[str] = None):
        """Constructs ShadowBots with provided name"""

        shadowbot: ShadowBot = ShadowBot()
        shadowbot.rename(new_name=name)

        return shadowbot

    def observe(self, bot: ShadowBot):
        """Creates and registers a ShadowObserver"""

        observer: ShadowObserver = ShadowObserver()

        # Register observer to start receiving notifications
        bot.register(observer=observer)

        return observer

    def unobserve(self, bot: ShadowBot, observer: ShadowObserver):
        """Deregisters ShadowObserver from ShadowBot notification list"""

        bot.deregister(observer=observer)

        return observer
