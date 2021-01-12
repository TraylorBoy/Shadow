"""Proxy to the ShadowNetwork interface"""

import time

from functools import partial

from datetime import datetime

from typing import Any, Dict, Optional, Tuple, List

from shadow.core.interface import IShadowNetwork, IShadowBot
from shadow.core.network import ShadowNetwork
from shadow.core.bot import ShadowBot
from shadow.helpers import Borg

from loguru import logger

def client_log(record):
    return record["name"] in ["shadow.client", "shadow.core"]

# Setup log file
logger.add(
    f"shadow/logs/client/{datetime.now().month}_{datetime.now().day}_{datetime.now().year}.log",
    rotation="500 MB",
    enqueue=True,
    filter=client_log
)

class ShadowNetworkProxy(IShadowNetwork):

    """ShadowNetwork Proxy class"""

    def __init__(self, host: str = "127.0.0.1", port: int = 0):
        """Instantiates the shadow network instance

        Args:
            host (str, optional): Host the server is running on. Defaults to "127.0.0.1".
            port (int, optional): Port the server is listening on. Defaults to 0.
        """

        self.network: ShadowNetwork = ShadowNetwork(host, port)

    def serve(self):
        """Start running the ServerBot

        Returns:
            [bool]: Server started successfully or not
        """

        self.network.serve()
        time.sleep(1)

        return self.alive()

    def kill(self):
        """Stops the running server instance

        Returns:
            [Tuple[str, Optional[Any]]]: Shutdown message received from the server
        """

        resp: Tuple[str, Optional[Any]] = self.network.kill()
        time.sleep(1)

        return resp

    def send(self, message: Tuple[str, Optional[Any]]):
        """Sends a message to the running server instance

        Args:
            message (Tuple[str, Optional[Any]]): Message to send to the server

        Returns:
            [Optional[Tuple[str, Optional[Any]]]]: Response received from the server
        """

        return self.network.send(message)

    def alive(self):
        """Checks if network is running

        Returns:
            [bool]: Network is alive
        """

        return self.network.alive()

    def status(self):
        """Checks if server is connected

        Returns:
            [bool]: Server is listening
        """

        return self.network.status()

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

class ShadowBotProxy(Borg, IShadowBot):

    """ShadowBot proxy class"""

    def __init__(self, shadowbot: ShadowBot):
        """Initizalises a proxy to the ShadowBot instance

        Args:
            shadowbot (ShadowBot): The instantiated ShadowBot instance to connect to
        """

        # Makes proxy a singleton instance
        self.__setup(shadowbot)

    def __setup(self, shadowbot: ShadowBot): # pragma: no cover
        """Setup singleton instance
        """

        super().__init__()

        ATTR: List[str] = ["bot", "events", "keep_alive"]

        setters: Dict[str, Any] = {
            "bot": shadowbot,
            "events": list(shadowbot.events.keys()),
            "keep_alive": False
        }

        for attribute in ATTR:
            if not hasattr(self, attribute):
                setattr(self, attribute, setters[attribute])

    # --------------------------------- Interface -------------------------------- #

    @logger.catch
    def request(self, event: str, task: Optional[str]):
        """Sends a request to the ShadowBot

        Args:
            event (str): Type of request to send
            task (Optional[str]): Task to send to the ShadowBot if the request type is "wait" or "perform"
        """

        if event not in self.events:
            logger.warning(f"Invalid event, {event}")
            logger.info(f"Valid events: {self.events}")
            return None

        self.bot.request(event, task)

    @logger.catch
    def response(self, task: str):
        """Check for a response from the ShadowBot

        Args:
            task (str): Task to retrieve the result for

        Returns:
            [Optional[Tuple[str, any]]]: Result from the requested task
        """

        return self.bot.response(task)

    @logger.catch
    def alive(self):
        """Checks if ShadowBot is alive

        Returns:
            [bool]: ShadowBot process is running or not
        """

        return self.bot.alive()

    @logger.catch
    def perform(self, task: str):
        """Sends a task to the ShadowBot to perform

        Args:
            task (str): Task to be executed
        """

        if not self.alive():
            logger.critical("ShadowBot is not running")
            return None

        self.request(event="perform", task=task)

    @logger.catch
    def wait(self, task: str):
        """Sends a wait event to the ShadowBot to wait for the given task to finish

        Args:
            task (str): Task to be executed
        """

        if not self.alive():
            logger.critical("ShadowBot is not running")
            return None

        self.request(event="wait", task=task)

    @logger.catch
    def kill(self):
        """Stops the running ShadowBot instance
        """

        if not self.alive():
            logger.critical("ShadowBot is not running")
            return None

        self.bot.stop()

    @logger.catch
    def jutsu(self, task: str):
        """Performs, waits, and then returns the result of the given task

        Args:
            task (str): Task to retrieve the result for

        Returns:
            [Optional[Tuple[str, any]]]: Result from the requested task
        """

        self.perform(task)
        self.wait(task)

        response: Tuple[str, Any] = self.response(task)

        return response

    # ---------------------------------- Context --------------------------------- #

    def setup(self):
        """Setup context manager
        """

        if not self.bot.alive(): self.bot.start()

    def __enter__(self):
        """Gives access to the context manager
        """

        return self.setup()

    def __exit__(self, *_):
        """Cleans up the context manager
        """

        if not self.keep_alive and self.alive(): self.kill()

