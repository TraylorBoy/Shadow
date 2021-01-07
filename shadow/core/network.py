"""Creates a network of ShadowBots"""

import dill
import socket


from datetime import datetime

from functools import partial
from typing import Optional, Any, Dict, Tuple, List

from shadow.helpers import Borg
from shadow.core.interface import IShadowNetwork
from shadow.server import ShadowServer
from shadow.core.bot import ShadowBot

from loguru import logger

def network_log(record):
    return record["name"] in ["shadow.server"]

# Setup log file
logger.add(
    f"shadow/logs/server/{datetime.now().month}_{datetime.now().day}_{datetime.now().year}.log",
    rotation="500 MB",
    enqueue=True,
    filter=network_log
)

class ShadowNetwork(Borg, IShadowNetwork):

    """Manages ShadowBots and the server"""

    def __init__(self, host: str = "127.0.0.1", port: int = 0):
        """Initializes shared state and properties between each instance

        Args:
            host (str, optional): Host to run server on. Defaults to "127.0.0.1".
            port (int, optional): Port to connect to. Defaults to 0.
        """

        super().__init__()

        if not hasattr(self, "host"):
            self.host: str = host

        if not hasattr(self, "port"):
            self.port: int = port

        if not hasattr(self, "server"):
            self.server: ShadowServer = ShadowServer(host, port)

        if not hasattr(self, "bot"):
            server_tasks: Dict[str, partial] = {
                "serve": partial(self.server.serve),
                "shutdown": partial(self.stop),
                "status": partial(self.server.alive)
            }

            self.bot: ShadowBot = ShadowBot(name="ServerBot", tasks=server_tasks)
            self.bot.soul.name = "ServerBot"

    def send(self, message: Tuple[str, Optional[Any]]):
        """Connects to the server and writes the message

        Args:
            message (Tuple[str, Optional[Any]]): Message to write to the server

        Returns:
            [Optional[Tuple[str, Optional[Any]]]]: Response from the server
        """

        if not self.alive():
            logger.critical("ServerBot is not alive")
            return None

        resp: Optional[Tuple[str, Optional[Any]]] = None

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # "Address already in use" fix
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Open a connection to the server
            sock.connect((self.host, self.port))

            # Send over the message
            sock.sendall(dill.dumps(message))

            # Read response
            resp = dill.loads(sock.recv(1024))

            logger.info(f"Received a response: {resp}")

        return resp

    def serve(self):
        """Start serving with the ServerBot
        """

        self.bot.start()
        self.bot.request(type="perform", task="serve")

    def stop(self):
        """Sends a shutdown signal to the server

        Returns:
            [Optional[Tuple[str, Optional[Any]]]]: Response from the server
        """

        if not self.alive():
            logger.critical("ServerBot is not alive")
            return None

        return self.send(message=("shutdown", None))

    def kill(self):
        """Stop serving with the ServerBot
        """

        if not self.alive():
            logger.critical("ServerBot is not alive")
            return None

        self.bot.request(type="perform", task="shutdown")
        self.bot.request(type="wait", task="shutdown")
        self.bot.stop()

    def alive(self):
        """Checks if ServerBot is alive

        Returns
            [bool]: ServerBot is alive or not
        """

        return self.bot.alive()

    def status(self):
        """Checks if server process is listening for requests

        Returns:
            [Optional[Any]]: Server status response
        """

        if not self.alive():
            logger.critical("ServerBot is not alive")
            return None

        self.bot.request(type="perform", task="status")
        self.bot.request(type="wait", task="status")

        # Get the response from the server
        _, result = self.bot.response()

        return result
