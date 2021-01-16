"""Request class for handling requests sent from the client"""

from shadow.core.bot import ShadowBot, Needles, Needle

from functools import partial
from typing import Optional, Any, Dict, Callable, Tuple, List

from loguru import logger

class ShadowRequest(object):

    """Server request handler

    Runs everytime there is a new connection
    """

    def __init__(self):
        """Initializes the request handler
        """

        self.needles: Needles = Needles()

    def __shutdown(self, _: Optional[Any]):
        """Processes shutdown request sent from the client
        """

        # Cleanup
        self.needles.save()

        return ("SHUTDOWN", True)

    def __needles(self, _: Optional[Any]):
        """Sends over all ShadowBot id's and their tasks to the client

        Returns
            [Tuple[str, Optional[Any]]]: Response to the client
        """

        resp: Dict[str, Needle] = {}
        with self.needles:
            resp = self.needles.pool

        logger.info(f"Sending over needles data: {resp}")
        return ("NEEDLES", resp)

    def __build(self, data: Optional[Any]):
        """Builds a ShadowBot and sews it

        Args:
            data (Optional[Any]): ShadowBot name and tasks

        Returns:
            [Tuple[str, Optional[Any]]]: Response to the client
        """

        essence: Needle = data

        logger.info(f"Building ShadowBot with essence: {essence}")

        successful: bool = False
        with self.needles:
            self.needles.sew(essence)

            name, _, _ = essence
            successful = self.needles.check(name)

        return ("BUILD", successful)

    def handle(self, message: Tuple[str, Optional[Any]]):
        """Processes messages sent from the client

        Args:
            message (Tuple[str, Optional[Any]]): Message sent from the client

        Returns:
            [Tuple[str, Optional[Any]]]: Response to the client
        """

        events: Dict[str, Callable] = {
            "build": self.__build,
            "needles": self.__needles,
            "shutdown": self.__shutdown
        }

        event, data = message

        logger.info(f"Processing request: {event}, {data}")

        if event in events.keys():
            return events[event](data)

        else:
            logger.warning(f"Invalid message received: {message}")

            # Echo back the invalid message
            return ("INVALID", message)

