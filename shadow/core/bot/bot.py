"""Task Manager"""

import time
import multiprocessing as mp

from functools import partial
from typing import Dict, Any, Optional, Callable, Tuple

from .clone import ShadowClone
from .interface import IShadowBot
from .needle import Needle

from loguru import logger

class ShadowBot(IShadowBot):

    """Master class for running tasks performed by ShadowClones (slaves)"""

    def __repr__(self):
        """Returns a string representation of the ShadowBot instance"""

        return f"{self.name}, {self.tasks} - {self.state}"

    def __init__(self, name: str, tasks: Dict[str, partial], history: Dict[str, Optional[Any]] = {}):
        """Sets ShadowBot's default properties and state

        Args:
            name (str): Name to identify the ShadowBot on the network
            tasks (Dict[str, partial]): Tasks for the ShadowBot to perform
        """

        self.name: str = name
        self.tasks: Dict[str, partial] = tasks
        self.state: str = "off"
        self.events: Dict[str, Callable] = {
            "kill": self.kill,
            "perform": self.perform,
            "wait": self.wait,
            "result": self.result
        }

        self.context: Any = mp.get_context(method="spawn")
        self.soul: self.context.Process = self.context.Process(target=self.core, name=self.name, daemon=True)
        self.results: self.context.Queue = self.context.Queue()
        self.requests: self.context.Queue = self.context.Queue()
        self.responses: self.context.Queue = self.context.Queue()

        self.clones: Dict[str, ShadowClone] = {}
        self.history: Dict[str, Optional[Any]] = history

# --------------------------------- Interface -------------------------------- #

    def request(self, event: str, task: Optional[str]):
        """Sends a request to the ShadowBot

        Args:
            event (str): Type of request to send
            task (Optional[str]): Task to send to the ShadowBot if the request type is "wait" or "perform"
        """

        if not self.alive():
            logger.critical("ShadowBot is not running")
            return None

        self.requests.put((event, task))
        time.sleep(1)

    def response(self, task: str):
        """Check for a response from the ShadowBot

        Args:
            task (str): Task to retrieve the result for

        Returns:
            [Optional[Tuple[str, any]]]: Result from the requested task
        """

        self.request(event="wait", task=task)
        self.request(event="result", task=task)

        if self.responses.empty():
            logger.warning("No responses were found from ShadowBot")
            return None

        response: Tuple[str, Any] = self.responses.get()

        logger.info(f"Result compiled: {response}")

        return response

    def alive(self, task: Optional[str] = None): # pragma: no cover
        """Checks if ShadowBot process has started

        Will check if ShadowClone thread is still running if task is given instead.

        Args:
            task (Optional[str]): ShadowClone thread to check for. Defaults to None.

        Returns:
            [bool]: ShadowBot/ShadowClone is running or not
        """

        if task is None: return self.soul.is_alive()

        if task not in self.tasks.keys():
            logger.critical(f"{task} not found")
            return None

        if task not in self.clones.keys():
            logger.warning(f"{task} not performed")
            return None

        return self.clones[task].is_alive()

    def perform(self, task: str):
        """Performs task retrieved from the task queue

        Args:
            task (str): Task to be executed
        """

        if task not in self.tasks.keys():
            logger.critical(f"{task} not found")
            return None

        logger.info(f"Performing task: {task}")

        # Create and start the ShadowClone's thread
        self.jutsu(task)

    def wait(self, task: str):
        """Waits for ShadowClone to finish performing the task

        Args:
            task (str): Task to be executed
        """

        if task not in self.tasks.keys():
            logger.critical(f"{task} not found")
            return None

        logger.info(f"Waiting for {task} to finish")

        try:
            self.clones[task].join(timeout=10)
            logger.info(f"{task} was successfully joined")
        except mp.TimeoutError: # pragma: no cover
            logger.critical(f"{task} timed out while waiting for it to finish")
            return None

    def jutsu(self, task: str):
        """Creates a ShadowClone worker thread that performs the task

        Args:
            task (str): Task to be executed
        """

        if task not in self.tasks.keys():
            logger.critical(f"{task} not found")
            return None

        logger.info("~Shadow Clone Jutsu~")

        self.clones[task] = ShadowClone(name=task, args=(self.tasks[task], self.results))
        self.clones[task].start()

    def kill(self):
        """Transitions ShadowBot state from on to off
        """

        self.state = "off"
        self.responses.put(("KILL", True))

# ----------------------------------- State ---------------------------------- #

    def start(self):
        """Transitions state from off to on and starts the ShadowBot's process

        The ShadowBot opens a socket on the given port and starts listening for incoming tasks.

        Args:
            port (int): Port to listen on
        """

        if self.alive():
            logger.warning("Already running")
            return None

        logger.info("Starting up")

        self.state = "on"

        try:
            self.soul.start()
        except AssertionError:
            # Process already ran, set a new one
            self.restart()
            self.start()

    def stop(self):
        """Stop the running ShadowBot process"""

        if not self.alive():
            logger.warning("ShadowBot is already stopped")
            return None

        logger.info("Stopping")

        # Send a kill signal
        self.requests.put(("kill", None))

        # Wait for process to rejoin
        self.soul.join(timeout=10)

    def restart(self):
        """Re-instantiates the ShadowBot's process"""

        logger.info("Restarting")

        if self.alive(): self.stop()

        self.__init__(self.name, self.tasks)

        self.start()

# ---------------------------------- Core --------------------------------- #

    @logger.catch
    def core(self):
        """Method is called when the process is started"""

        while True:
            if self.state == "off":  # pragma: no cover
                logger.warning("Shutting down")
                break

            if not self.requests.empty():
                event, task = self.requests.get()
                logger.info(f"Request received: ({event}, {task})")

                if event in self.events.keys():
                    logger.info(f"Handling event: {event}")
                    self.events[event]() if event not in ["perform", "wait", "result"] else self.events[event](task)

                else: # pragma: no cover
                    logger.critical(f"Unable to handle event: {event}")
                    continue

                logger.info(f"Successfully handled event: {event}")

        logger.info("ShadowBot stopped successfully")

    def compile(self):
        """Checks for results in the results queue and stores them in the history
        """

        while not self.results.empty():
            task, result = self.results.get()
            logger.debug(f"{result} compiled for {task}")

            self.history[task] = result

    def result(self, task: str):
        """Retrieves the compiled result for the given task from the history

        Args:
            task (str): Task to retrieve the result for

        Returns:
            [Optional[Any]]: Result from the performed task
        """

        if task not in self.tasks.keys():
            logger.critical(f"{task} not found")
            return None

        self.compile()

        if task not in self.history.keys(): # pragma: no cover
            logger.warning(f"Result for {task} not found")
            return None

        self.responses.put((task, self.hist(task)))

    def hist(self, task: str):
        """Retrieve the result for a task from the history

        Args:
            task (str): Task to retrieve the result for
        """

        if task not in self.history.keys():
            logger.warning(f"Result for {task} not found")
            return None

        return self.history[task]

    @property
    def essence(self):
        """ShadowBot's essence property

        Returns:
            [NamedTuple]: The ShadowBot's name, tasks, and history used to save and load the instance on the network
        """

        return Needle(self.name, self.tasks, self.history)
