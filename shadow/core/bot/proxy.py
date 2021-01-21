"""Proxy to the ShadowNetwork interface"""

from datetime import datetime

from typing import Any, Optional, Tuple, List

from .interface import IShadowBot
from .bot import ShadowBot
from .needles import Needle

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


class ShadowBotProxy(IShadowBot):

    """ShadowBot proxy class"""

    def __init__(self, essence: Needle):
        """Initizalises a proxy to the ShadowBot instance

        Args:
            shadowbot (ShadowBot): The instantiated ShadowBot instance to connect to
        """

        name, tasks, history = essence
        self.bot: ShadowBot = ShadowBot(name, tasks, history)
        self.events: List[str] = list(self.bot.events.keys())
        self.keep_alive: bool = False

    # ---------------------------------- Context --------------------------------- #

    def setup(self):
        """Setup context manager
        """

        if not self.bot.alive(): self.bot.start()

    def __enter__(self):
        """Gives access to the context manager
        """

        self.setup()
        return self

    def __exit__(self, *_):
        """Cleans up the context manager
        """

        if not self.keep_alive and self.alive(): self.kill()


    # --------------------------------- Interface -------------------------------- #

    @logger.catch
    def request(self, event: str, task: Optional[str] = None):
        """Sends a request to the ShadowBot

        Args:
            event (str): Type of request to send
            task (Optional[str]): Task to send to the ShadowBot if the request type is "wait" or "perform". Defaults to None.
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
            [Optional[Any]]: Result from the requested task
        """

        self.perform(task)
        self.wait(task)

        response: Optional[Any] = self.response(task)

        return response
