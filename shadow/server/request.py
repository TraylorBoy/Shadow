"""Request class for handling requests sent from the client"""

from shadow.core.needles import Needles
from shadow.core.bot import ShadowBot

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

        logger.info("Sending over needles data")

        response: List[Tuple[str, Dict[str, partial]]] = []

        for needle in self.needles:
            logger.debug(needle)
            response.append((needle.id, needle.essence))

        return ("NEEDLES", response)

    def __build(self, data: Optional[Any]):
        """Builds a ShadowBot and sews it

        Args:
            data (Optional[Any]): ShadowBot name and tasks

        Returns:
            [Tuple[str, Optional[Any]]]: Response to the client
        """

        name, tasks = data

        logger.info(f"Building ShadowBot: {name}, {tasks}")

        shadowbot: ShadowBot = ShadowBot(name, tasks)

        self.needles.sew(bot=shadowbot)

        return ("BUILD", shadowbot.essence)

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

