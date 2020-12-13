"""Entry point to the Shadow project"""

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

    """Interface for making ShadowBots and building the ShadowNetwork"""

    def build(self, name: Optional[str] = None):
        """Constructs ShadowBots with provided args"""

        # Create ShadowBot
        shadowbot: ShadowBot = ShadowBot()

        # Build part
        shadowbot.rename(new_name=name)

        # Return product
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

        logger.info(f"Observer deregistered for {bot.name}")
