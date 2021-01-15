"""Server instance for the ShadowNetwork"""

import socket
import dill

from shadow.server.request import ShadowRequest
from shadow.core.helpers import Borg

from typing import Tuple, Optional, List, Any, Dict
from loguru import logger

class ShadowServer(Borg):

    """TCP Server class"""

    def __init__(self, host: str, port: int):
        """Sets default server state and properties

        Args:
            host (str): Host to connect to
            port (int): Port to listen on
        """

        self.__setup(host, port)

    def __setup(self, host: str, port: int):
        """Initializes singleton instance

        Args:
            host (str): Host to connect to
            port (int): Port to listen on
        """

        super().__init__()

        ATTR: List[str] = ["addr", "sock", "handler", "__alive"]

        setters: Dict[str, Any] = {
            "addr": (host, port),
            "sock": None,
            "handler": ShadowRequest(),
            "__alive": False
        }

        for attribute in ATTR:
            if not hasattr(self, attribute):
                setattr(self, attribute, setters[attribute])

    def __read(self, conn: Any):
        """Processes data sent from the client

        Args:
            conn (Any): Client connection object
        """

        message: Tuple[str, Optional[Any]] = dill.loads(conn.recv(1024))

        logger.info(f"Received message: {message}")

        # Handle request
        event, data = self.handler.handle(message)

        if event == "SHUTDOWN": self.__alive = False

        # Send response for handled request
        self.__write(conn, event, data)

    def __write(_, conn: Any, event: str, data: Optional[Any]):
        """Send a response to the client

        Args:
            conn (Any): Client connection object
            event (str): Event processed
            data (Optional[Any]): Data to send to the client
        """

        logger.info(f"Sending response to client: {event}, {data}")

        message: Tuple[str, Optional[Any]] = (event, data)

        conn.sendall(dill.dumps(message))

    def assign(self):
        """Attempts to open a socket on the port set during instantiation
        """

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # "Address already in use" fix
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Connect and listen for incoming connections
        try:
            self.sock.bind(self.addr)
        except socket.error as msg:
            logger.critical(f"Failed to bind socket: {msg}")
            self.sock.close()
            self.sock = None
            return None

        logger.info(f"Socket created, listening on port: {self.addr[1]}")
        self.sock.listen(5)

    def listen(self):
        """Listen for incoming requests from the client
        """

        while True:
            if not self.__alive:
                logger.warning("Closing serving")
                break

            # Open connection
            conn, addr = self.sock.accept()

            with conn:
                logger.info(f"Connected to: {addr}")

                # Process request
                self.__read(conn)

    def serve(self):
        """Starts listening for incoming requests
        """

        # Find an open socket to connect to
        self.assign()

        # No socket found
        if self.sock is None:
            return None

        # Set state
        self.__alive = True

        # Start receving requests
        self.listen()

        # Server shutdown, cleanup
        self.sock.close()

    def alive(self):
        """Checks if server is accepting new connections

        Returns:
            [bool]: Server is alive or not
        """

        return self.__alive



