"""Interface for interacting with the application"""

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from loguru import logger

from shadow.proxy import ShadowProxy

# Setup log file
logger.add(
    f"shadow/logs/{datetime.now().month}_{datetime.now().day}_{datetime.now().year}.log",
    rotation="500 MB",
    enqueue=True,
)


class Shadow:

    """Application entry point"""

    def build(
        self, name: Optional[str] = None, tasks: Optional[Dict[str, Tuple[Any]]] = None
    ):
        """Creates a proxy for interacting with ShadowBot after setting it up

        Args:
            name (Optional[str], optional): Name of the ShadowBot. Defaults to None.
            tasks (Optional[Dict[str, Tuple[Any]]], optional): Functions for the ShadowBot to call by signal. Defaults to None.

        Returns:
            [ShadowProxy]: Instansiated proxy object for the constructed ShadowBot
        """

        proxy: ShadowProxy = ShadowProxy()

        proxy = self.setup(proxy=proxy, name=name, tasks=tasks)

        return proxy

    def edit(
        self,
        proxy: ShadowProxy,
        signal: str = None,
        remove: bool = False,
        task: Optional[Tuple[Any]] = None,
        name: Optional[str] = None,
    ):
        """Edits constructed ShadowBot attached to the given proxy

        Args:
            proxy (ShadowProxy): Proxy to the ShadowBot that is being configured
            signal (str, optional): Signal to add to the ShadowBot. Defaults to None.
            remove (bool, optional): Remove the signal being passed. Defaults to False.
            task (Optional[Tuple[Any]], optional): Add the task with the signal to the ShadowBot. Defaults to None.
            name (Optional[str], optional): Change the name of the ShadowBot. Defaults to None.

        Returns:
            [ShadowProxy]: Instansiated proxy object with the reconfigured ShadowBot
        """

        if name is not None:
            proxy.bot.name = name

        elif signal is not None:
            if remove:
                proxy.bot.remove_task(signal=signal)

            else:
                proxy.bot.add_task(
                    signal=signal, task=task
                ) if task is not None else None

            return proxy

    def setup(
        self,
        proxy: ShadowProxy,
        name: Optional[str] = None,
        tasks: Optional[Dict[str, Tuple[Any]]] = None,
    ):
        """Configures ShadowBot attached to the given proxy

        Args:
            proxy (ShadowProxy): Proxy to the ShadowBot that is being setup
            name (Optional[str], optional): Name to set for the ShadowBot
            tasks (Optional[Dict[str, Tuple[Any]]], optional): Functions for the ShadowBot to call by signal. Defaults to None.

        Returns:
            [ShadowProxy]: Instansiated proxy object with the reconfigured ShadowBot
        """

        if name is not None:
            proxy.bot.name = name

        if tasks is not None:
            for _signal, _task in tasks.items():
                proxy.bot.add_task(signal=_signal, task=_task)

        return proxy
