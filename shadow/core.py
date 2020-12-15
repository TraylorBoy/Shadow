"""Facade for interacting with the application"""

from datetime import datetime
from typing import Optional

from loguru import logger

from shadow.proxy import ShadowProxy

from typing import Any, Dict, Optional, Tuple

# Setup log file
logger.add(
    f"shadow/logs/{datetime.now().month}_{datetime.now().day}_{datetime.now().year}.log",
    rotation="500 MB",
    enqueue=True,
)


class Shadow:

    """Entry point"""

    def build(self, name: Optional[str] = None, tasks: Optional[Dict[str, Tuple[Any]]] = None):
        """Creates a proxy for interacting with ShadowBot after setting it up"""

        proxy: ShadowProxy = ShadowProxy()

        proxy.setup(name=name, tasks=tasks)

        return proxy

    def edit(self, proxy: ShadowProxy, signal: str = None, remove: bool = False, task: Optional[Tuple[Any]] = None, name: Optional[str] = None):
        """Edits constructed ShadowBot attached to proxy"""

        if name is not None:
            proxy.bot.name = name

        elif signal is not None:
            if remove:
                proxy.bot.remove_task(signal=signal)

            else:
                proxy.bot.add_task(signal=signal, task=task)

            return proxy
