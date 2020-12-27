"""Proxy to the ShadowNetwork interface"""

import asyncio

from functools import partial

from typing import Any, Dict, Optional

from shadow.interface import IShadowNetwork
from shadow.network import ShadowNetwork

class ShadowProxy(IShadowNetwork):

    """ShadowNetwork Proxy class"""

    def __init__(self, host: str = "127.0.0.1", port: int = 8888):
        """Instantiates the shadow network instance

        Args:
            host (str, optional): Host the server is running on. Defaults to "127.0.0.1".
            port (int, optional): Port the server is listening on. Defaults to 8888.
        """

        self.network: ShadowNetwork = ShadowNetwork(host, port)

    def serve(self): # pragma: no cover
        """Start running the server
        """

        asyncio.run(self.network.serve())

    def send(self, message: Dict[str, Optional[Any]]): # pragma: no cover
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

        response: Any = asyncio.run(self.network.send(message))

        return response

    def kill(self): # pragma: no cover
        """Stop running the server
        """

        asyncio.run(self.network.kill())

    def build(self, name: str, tasks: Dict[str, partial]):
        """Sends the server information to build a ShadowBot

        Args:
            name (str): Name to identify the ShadowBot
            tasks (Dict[str, partial]): Tasks for the ShadowBot to perform on the server
        """

        asyncio.run(self.network.build(name, tasks))
