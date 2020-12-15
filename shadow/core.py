"""Facade for interacting with the application"""

from datetime import datetime
from typing import Optional

from loguru import logger

from shadow.bot import ShadowBot
from shadow.proxy import ShadowProxy
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
        """Constructs ShadowBots and returns a proxy for interacting with them"""

        proxy: ShadowProxy = ShadowProxy()
        proxy.bot.name = name

        return proxy

