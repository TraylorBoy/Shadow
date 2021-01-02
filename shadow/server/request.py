"""Request class for handling requests sent from the client"""

import dill
import socketserver

from typing import Optional, Any, Dict, Callable, Tuple

from loguru import logger

class ShadowRequest(socketserver.BaseRequestHandler):

    """Server request handler

    Runs everytime there is a new connection
    """

    def __shutdown(self, _: Optional[Any] = None):
        """Closes the running server
        """

        self.__respond(event="SHUTDOWN", data=True)

        self.server.server_close()

    def __respond(self, event: str, data: Optional[Any]):
        """Sends a response to the client

        Args:
            response (Tuple[str, Optional[Any]]): Message to send back to the client after processing their request
        """

        logger.info(f"Sending response to client: {event}, {data}")

        self.request.sendall(dill.dumps((event, data)))

    def __process(self, message: Tuple[str, Optional[Any]]):
        """Processes messages sent from the client

        Args:
            message (Tuple[str, Optional[Any]]): Message sent from the client
        """

        events: Dict[str, Callable] = {
            "shutdown": self.__shutdown
        }

        event, data = message

        logger.info(f"Processing request: {event}, {data}")

        if event in events.keys():
            events[event](data)

            self.server.server_close()

        else:
            logger.warning(f"Invalid message received: {message}")

    def handle(self):
        """Message handler"""

        data: Any = self.request.recv(1024)

        message: Dict[str, Optional[Any]] = dill.loads(data)

        logger.info(f"Received message: {message}")

        self.__process(message)
