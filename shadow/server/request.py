"""Request class for handling requests sent from the client"""

import dill
import socketserver

from threading import Thread, current_thread

from typing import Optional, Any, Dict

from loguru import logger

class ShadowRequest(socketserver.BaseRequestHandler):

    """Server request handler

    Runs everytime there is a new connection
    """

    def __respond(self, response: Dict[str, Optional[Any]]):
        """Sends a response to the client

        Args:
            response (Dict[str, Optional[Any]]): Message to send back to the client after processing their request
        """

        self.request.sendall(dill.dumps(response))

    def __process(self, message: Dict[str, Optional[Any]]):
        """Processes messages sent from the client

        Args:
            message (Dict[str, Optional[Any]]): Message sent from the client
        """

        response: Dict[str, Optional[Any]] = {
        }

        logger.info(f"Processing request: {message['event']}")

        if message["event"] == "shutdown":

            response["event"] = "SHUTDOWN"
            response["data"] = True

            self.__respond(response)

            self.server.server_close()

        else:
            logger.warning(f"Invalid message received: {message}")

    def handle(self):
        """Message handler"""

        t: Thread = current_thread()

        data: Any = self.request.recv(1024)

        message: Dict[str, Optional[Any]] = dill.loads(data)

        logger.info(f"{t} - Received message: {message}")

        self.__process(message)
