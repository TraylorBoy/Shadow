"""Creates a network of ShadowBots"""

import dill
import socket

from datetime import datetime

from typing import Optional, Any, Dict, Tuple

from shadow.helpers import Borg
from shadow.interface import IShadowNetwork
from shadow.server import ShadowRequest, ShadowServer
from shadow.needles import Needles

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

    def __init__(self, host: str = "localhost", port: int = 0):
        """Initializes shared state and properties between each instance

        Args:
            host (str, optional): Host to run server on. Defaults to "127.0.0.1".
            port (int, optional): Port to connect to. Defaults to 8888.
        """

        super().__init__()

        if not hasattr(self, "host"):
            self.host: str = host

        if not hasattr(self, "port"):
            self.port: int = port

        if not hasattr(self, "server"):
            self.server: ShadowServer = ShadowServer((host, port), ShadowRequest)

            self.server.allow_reuse_address = True

        if not hasattr(self, "sock"):
            self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if not hasattr(self, "needles"):
            self.needles: Needles = Needles()

    def __write(self, message: Tuple[str, Optional[Any]]):
        """Connects to the server and writes the message

        Args:
            message (Tuple[str, Optional[Any]]): Message to write to the server
        """

        self.sock.connect((self.host, self.port))
        self.sock.sendall(dill.dumps(message))

        return self.__read()

    def __read(self):
        """Reads a response sent from the server

        Args:
            sock (socket.socket): Opened socket connection from writer
        """

        data: Any = self.sock.recv(1024)

        response: Dict[str, Optional[Any]] = dill.loads(data)

        self.sock.close()

        return response

    def serve(self):
        """Start running the server instance on a seperate thread
        """

        with self.server:
            # Create the server thread and start running it in the background

            self.host, self.port = self.server.server_address

            logger.info(f"Serving on {self.host}:{self.port}")

            self.server.serve_forever()

    def kill(self):
        """Stops the running server instance
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

        with self.server:
            return self.__write(message)
