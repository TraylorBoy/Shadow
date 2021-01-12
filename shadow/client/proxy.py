"""Proxy to the ShadowNetwork interface"""

import socket
import dill
import time

from functools import partial

from datetime import datetime

from typing import Any, Dict, Optional, Tuple, Callable

from shadow.core.interface import IShadowNetwork, IShadowBot
from shadow.core.network import ShadowNetwork
from shadow.core.bot import ShadowBot

from loguru import logger

def client_log(record):
    return record["name"] in ["shadow.client", "shadow.core"]

# Setup log file
logger.add(
    f"shadow/logs/client/{datetime.now().month}_{datetime.now().day}_{datetime.now().year}.log",
    rotation="500 MB",
    enqueue=True,
    filter=client_log
)

class ShadowNetworkProxy(IShadowNetwork):

    """ShadowNetwork Proxy class"""

    def __init__(self, host: str = "127.0.0.1", port: int = 0):
        """Instantiates the shadow network instance

        Args:
            host (str, optional): Host the server is running on. Defaults to "127.0.0.1".
            port (int, optional): Port the server is listening on. Defaults to 0.
        """

        self.network: ShadowNetwork = ShadowNetwork(host, port)

    def serve(self):
        """Start running the ServerBot

        Returns:
            [bool]: Server started successfully or not
        """

        self.network.serve()
        time.sleep(1)

        return self.alive()

    def kill(self):
        """Stops the running server instance

        Returns:
            [Tuple[str, Optional[Any]]]: Shutdown message received from the server
        """

        resp: Tuple[str, Optional[Any]] = self.network.kill()
        time.sleep(1)

        return resp

    def send(self, message: Tuple[str, Optional[Any]]):
        """Sends a message to the running server instance

        Args:
            message (Tuple[str, Optional[Any]]): Message to send to the server

        Returns:
            [Optional[Tuple[str, Optional[Any]]]]: Response received from the server
        """

        return self.network.send(message)

    def alive(self):
        """Checks if network is running

        Returns:
            [bool]: Network is alive
        """

        return self.network.alive()

    def status(self):
        """Checks if server is connected

        Returns:
            [bool]: Server is listening
        """

        return self.network.status()

    def build(self, name: str, tasks: Dict[str, partial]):
        """Builds a ShadowBot on the network

        Args:
            name (str): [description]
            tasks (Dict[str, partial]): [description]

        Returns:
            [Optional[Tuple[str, Optional[Any]]]: Response received from the server
        """

        data: Tuple[str, Dict[str, partial]] = (name, tasks)

        return self.send(message=("build", data))


# TODO: Make proxy context manager
class ShadowBotProxy(IShadowBot):

    """ShadowBot proxy class"""

    def __init__(self, shadowbot: ShadowBot):
        """Initizalises a proxy to the ShadowBot instance

        Args:
            shadowbot (ShadowBot): The instantiated ShadowBot instance to connect to
        """

        self.bot: ShadowBot = shadowbot
        self.events: self.bot.events.keys()

    def request(self, event: str, task: Optional[str]):
        """Sends a request to the ShadowBot

        Args:
            event (str): Type of request to send
            task (Optional[str]): Task to send to the ShadowBot if the request type is "wait" or "perform"
        """

        self.bot.request(event, task)

    def response(self, task: str):
        """Check for a response from the ShadowBot

        Args:
            task (str): Task to retrieve the result for

        Returns:
            [Optional[Tuple[str, any]]]: Result from the requested task
        """

        return self.bot.response(task)
