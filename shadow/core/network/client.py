"""Server client class"""

import socket
import dill

from typing import Tuple, Optional, Any
from loguru import logger

class ShadowClient(object):

    """Connects and communicates with the ShadowServer"""

    def __init__(self, host: str, port: int):
        """Instatites the client with the server host and port

        Args:
            host (str): Host server is connected to
            port (int): Port server is listening on
        """

        self.addr: Tuple[str, int] = (host, port)

    def send(self, message: Tuple[str, Optional[Any]]):
        """Connects to the server and writes the message

        Args:
            message (Tuple[str, Optional[Any]]): Message to write to the server

        Returns:
            [Optional[Tuple[str, Optional[Any]]]]: Response from the server
        """

        resp: Optional[Tuple[str, Optional[Any]]] = None

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # "Address already in use" fix
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Open a connection to the server
            sock.connect(self.addr)

            # Send over the message
            sock.sendall(dill.dumps(message))

            # Read response
            resp = dill.loads(sock.recv(1024))

            logger.info(f"Received a response: {resp}")

        return resp
