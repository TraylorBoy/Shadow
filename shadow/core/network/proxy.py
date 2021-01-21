"""Proxy to the ShadowNetwork interface"""

import time

from functools import partial

from datetime import datetime

from typing import Any, Dict, Optional, Tuple

from .interface import IShadowNetwork
from .network import ShadowNetwork

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

    def __init__(self, host: str, port: int):
        """Instantiates the shadow network instance

        Args:
            host (str, optional): Host the server is running on. Defaults to "127.0.0.1".
            port (int, optional): Port the server is listening on. Defaults to 0.
        """

        self.network: ShadowNetwork = ShadowNetwork(host, port)

# --------------------------------- Interface -------------------------------- #

    def serve(self):
        """Start running the ServerBot

        Returns:
            [bool]: Server started successfully or not
        """

        is_successful: bool = self.network.serve()

        return is_successful

    def kill(self):
        """Stops the running server instance

        Returns:
            [bool]: Shutdown was successful or not
        """

        is_dead: bool = self.network.kill()

        return is_dead

    def alive(self):
        """Checks if network is running

        Returns:
            [bool]: Network is alive
        """

        return self.network.alive()

    def request(self, event: str, data: Optional[Any] = None):
        """Sends a message to the running server instance

        Args:
            event (str): Event to send
            data (Optional[Any]): Data associated with the request. Defaults to None.

        Returns:
            [Optional[Tuple[str, Optional[Any]]]]: Response received from the server
        """

        return self.network.request(event, data)


# ---------------------------------- Helpers --------------------------------- #

    @logger.catch
    def build(self, name: str, tasks: Dict[str, partial]):
        """Builds a ShadowBot on the network

        Args:
            name (str): [description]
            tasks (Dict[str, partial]): [description]

        Returns:
            [Optional[Tuple[str, Optional[Any]]]: Response received from the server
        """

        args: Tuple[str, Dict[str, partial]] = (name, tasks)

        return self.request(event="build", data=args)

