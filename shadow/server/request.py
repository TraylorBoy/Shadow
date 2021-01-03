"""Request class for handling requests sent from the client"""

import dill
import socketserver

from shadow.needles import Needles
from shadow.bot import ShadowBot

from typing import Optional, Any, Dict, Callable, Tuple, List

from loguru import logger

class ShadowRequest(socketserver.BaseRequestHandler):

    """Server request handler

    Runs everytime there is a new connection
    """

    def __build(self, data: Optional[Any]):
        """Builds a ShadowBot and sews it

        Args:
            data (Optional[Any]): ShadowBot name and tasks
        """

        name, tasks = data

        logger.info(f"Building ShadowBot: {name}, {tasks}")

        shadowbot: ShadowBot = ShadowBot(name, tasks)

        self.needles.sew(bot=shadowbot)

        self.__respond(event="BUILD", data=shadowbot.essence)

    def __shutdown(self, _: Optional[Any] = None):
        """Closes the running server
        """

        logger.warning("Shutting down server")

        self.__respond(event="SHUTDOWN", data=True)

        self.server.server_close()

    def __respond(self, event: str, data: Optional[Any]):
        """Sends a response to the client

        Args:
            response (Tuple[str, Optional[Any]]): Message to send back to the client after processing their request
        """

        logger.info(f"Sending response to client: {event}, {data}")

        message: Tuple[str, Optional[Any]] = (event, data)

        self.request.sendall(dill.dumps(message))

    def __process(self, message: Tuple[str, Optional[Any]]):
        """Processes messages sent from the client

        Args:
            message (Tuple[str, Optional[Any]]): Message sent from the client
        """

        events: Dict[str, Callable] = {
            "shutdown": self.__shutdown,
            "build": self.__build,
        }

        event, data = message

        logger.info(f"Processing request: {event}, {data}")

        if event in events.keys():
            events[event](data)

        else:
            logger.warning(f"Invalid message received: {message}")

    def setup(self):
        """Initializes the request handler
        """

        self.needles: Needles = Needles()

    def handle(self):
        """Message handler"""

        self.data = self.request.recv(1024).strip()

        message: Tuple[str, Optional[Any]] = dill.loads(self.data)

        logger.info(f"Received message: {message}")

        self.__process(message)

    def finish(self):
        """Called after handle method
        """

        logger.success("Message handled")


