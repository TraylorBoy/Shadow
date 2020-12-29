"""Proxy to the ShadowNetwork interface"""

import asyncio

from datetime import datetime

from functools import partial

from typing import Any, Dict, Optional

from shadow.interface import IShadowNetwork, IShadowBot
from shadow.network import ShadowNetwork
from shadow.bot import ShadowBot

from loguru import logger

def client_log(record):
    return record["name"] in ["shadow.proxy", "shadow.core"]

# Setup log file
logger.add(
    f"shadow/logs/client/{datetime.now().month}_{datetime.now().day}_{datetime.now().year}.log",
    rotation="500 MB",
    enqueue=True,
    filter=client_log
)

class ShadowProxy(IShadowNetwork):

    """ShadowNetwork Proxy class"""

    def __init__(self, host: str = "127.0.0.1", port: int = 8888):
        """Instantiates the shadow network instance

        Args:
            host (str, optional): Host the server is running on. Defaults to "127.0.0.1".
            port (int, optional): Port the server is listening on. Defaults to 8888.
        """

        self.network: ShadowNetwork = ShadowNetwork(host, port)
        self.bot: Optional[ShadowBot] = None

    def serve(self): # pragma: no cover
        """Start running the server
        """

        asyncio.run(self.network.serve())

    def send(self, message: Dict[str, Optional[Any]]):
        """Sends a message to the server

        Args:
            message (Dict[str, Optional[Any]]): Event and data to send to the server

            # Example
            -----------

            message = {
                "event": "build",
                "data": (name, tasks)
            }

            <ShadowProxy>.send(message)

        Returns:
            [Any]: Server response
        """

        logger.info(f"Sending message to server: {message}")

        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        response: Optional[Dict[str, Optional[Any]]] = loop.run_until_complete(self.network.send(message))

        logger.success(f"Response received: {response}")

        return response

    def kill(self):
        """Stop running the server
        """

        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        response: Optional[Dict[str, Optional[Any]]] = loop.run_until_complete(self.network.kill())

        return response

    def sew(self, name: str, tasks: Dict[str, partial]):
        """Sends the server information to build a ShadowBot

        Args:
            name (str): Name to identify the ShadowBot
            tasks (Dict[str, partial]): Tasks for the ShadowBot to perform on the server
        """

        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        response: Optional[Dict[str, Optional[Any]]] = loop.run_until_complete(self.network.sew(name, tasks))

        return response

    def retract(self, name: str):
        """Signals the network to remove the sewn ShadowBot

        Args:
            name (str): Name used to identify the ShadowBot
        """

        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        response: Optional[Dict[str, Optional[Any]]] = loop.run_until_complete(self.network.retract(name))

        return response

    def signal(self, name: str, event: str, task: str):
        """Sends a signal to the running ShadowBot process

        Args:
            name (str): Name used to identify the ShadowBot
            event (str): Event for ShadowBot to handle
            task (str): Task for ShadowBot to perform
        """

        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        response: Optional[Dict[str, Optional[Any]]] = loop.run_until_complete(self.network.signal(name, event, task))

        return response

    def link(self, name: str): # TODO
        """Sets up the proxy for direct communication with ShadowBot on the network

        Args:
            name (str): Name used to identify the ShadowBot
        """

        # Get needles from server
        needles: Dict[str, Optional[Any]] = self.network.send()
        pass

    def perform(self): # TODO

        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        pass

        """try:
            loop.run_until_complete(self.network.)"""
