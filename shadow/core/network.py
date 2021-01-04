"""Creates a network of ShadowBots"""

import dill
import socket
import time

from datetime import datetime

from functools import partial
from typing import Optional, Any, Dict, Tuple, List

from shadow.helpers import Borg
from shadow.core.interface import IShadowNetwork
from shadow.server import ShadowRequest, ShadowServer
from shadow.core.bot import ShadowBot

from loguru import logger

def network_log(record):
    return record["name"] in ["shadow.network", "shadow.needles", "shadow.bot", "shadow.clone", "shadow.server.request"]

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
            self.server: ShadowServer = ShadowServer((host, port), ShadowRequest, bind_and_activate=False)

            self.server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if not hasattr(self, "bot"):
            server_tasks: Dict[str, partial] = {
                "serve": partial(self.serve),
                "shutdown": partial(self.kill)
            }

            self.bot: ShadowBot = ShadowBot(name="ServerBot", tasks=server_tasks)

    def __write(self, message: Tuple[str, Optional[Any]]):
        """Connects to the server and writes the message

        Args:
            message (Tuple[str, Optional[Any]]): Message to write to the server
        """

        resp: Optional[Tuple[str, Optional[Any]]] = None

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

            # Open a connection to the server
            sock.connect((self.host, self.port))

            # Send over the message
            sock.sendall(dill.dumps(message))

            # Read response
            #data: List[Any] = []

            """while True:
                chunk = sock.recv(1024)

                if not chunk: break

                data.append(chunk)"""

            #resp = dill.loads(b"".join(data))
            resp = dill.loads(sock.recv(1024))

            logger.info(f"Received a response: {resp}")

        return resp

    def serve(self):
        """Start running the server instance on a seperate thread
        """

        with self.server:
            # Create the server thread and start running it in the background
            self.server.server_bind()
            self.server.server_activate()

            self.host, self.port = self.server.server_address

            logger.info(f"Serving on {self.host}:{self.port}")

            self.server.serve_forever()

    def kill(self):
        """Stops the running server instance and ServerBot
        """

        with self.server:
            self.server.shutdown()

    def send(self, message: Tuple[str, Optional[Any]]):
        """Sends a message to the running server instance

        Args:
            message (Tuple[str, Optional[Any]]): Message to send to the server

        Returns:
            [Optional[Tuple[str, Optional[Any]]]: Response received from the server
        """

        response: Optional[Tuple[str, Optional[Any]]] = self.__write(message)

        if message[0] == "shutdown": self.stop_server()

        return response

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

    def run_server(self):
        """Start serving with the ServerBot
        """

        self.bot.start()
        self.bot.request(type="perform", task="serve")

    def stop_server(self):
        """Stop serving with the ServerBot
        """

        self.bot.request(type="perform", task="shutdown")
        self.bot.stop()

    def alive(self):
        """Checks if ServerBot is alive

        Returns
            [bool]: ServerBot is alive or not
        """

        return self.bot.alive()
