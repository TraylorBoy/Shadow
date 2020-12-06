"""Entry point to the Shadow project"""

from datetime import datetime
from typing import Optional

from loguru import logger

from shadow.bot import ShadowBot
from shadow.helpers.observer import ShadowObserver

# Setup log file
logger.add(f"shadow/logs/{datetime.now()}.log")


class Shadow:

    """Interface for making ShadowBots and building the ShadowNetwork"""

    def __init__(self):
        """Instantiates sub-components"""

        # TODO
        self.network = None

    def make(self, name: Optional[str] = None):
        """Constructs ShadowBots with provided args"""

        # Create ShadowBot
        shadowbot: ShadowBot = ShadowBot()

        # Build part
        shadowbot.rename(new_name=name)

        logger.info(f"Constructed ShadowBot with name: {name}")

        # Return product
        return shadowbot

    def observe(self, bot: ShadowBot):
        """Creates and registers a ShadowObserver"""

        observer: ShadowObserver = ShadowObserver()

        # Register observer to start receiving notifications
        bot.state.register(observer=observer)

        logger.info(f"Observer registered for {bot.name}")

        return observer

    def unobserve(self, bot: ShadowBot, observer: ShadowObserver):
        """Deregisters ShadowObserver from ShadowBot notification list"""

        bot.state.deregister(observer=observer)

        logger.info(f"Observer deregistered for {bot.name}")
