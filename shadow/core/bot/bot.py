"""Task Manager"""

import time
import multiprocessing as mp
from threading import Thread

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
            "stop": self.kill,
            "perform": self.perform,
            "wait": self.wait,
            "generate": self.generate,
        }

        self.context: Any = mp.get_context(method="spawn")
        self.soul: self.context.Process = self.context.Process(target=self.core, name=self.name, daemon=True)
        self.results: self.context.Queue = self.context.Queue()
        self.requests: self.context.Queue = self.context.Queue()
        self.responses: self.context.Queue = self.context.Queue()
        self.compilation: self.context.Queue = self.context.Queue()

        self.clones: Dict[str, ShadowClone] = {}
        self.history: Dict[str, Optional[Any]] = history

# --------------------------------- Interface -------------------------------- #

    def request(self, event: str, task: Optional[str] = None):
        """Sends a request to the ShadowBot

        Args:
            event (str): Type of request to send
            task (Optional[str]): Task to send to the ShadowBot if the request type is "wait" or "perform". Defaults to None
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
            [Optional[Any]]: Result from the requested task
        """

        self.request(event="generate")
        time.sleep(1)

        if not self.responses.empty():
            try:

                response: Dict[str, Optional[Any]] = self.responses.get(timeout=10)

                if task not in response.keys(): # pragma: no cover
                    logger.warning(f"No responses were found for {task}")
                    return None

                logger.info(f"Result compiled: {response[task]}")

                return response[task]

            except mp.TimeoutError: # pragma: no cover
                logger.warning("Response timed out")
                return None

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
        self.requests.put(("stop", None))

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

        # Start compiler
        compiler: ShadowClone = ShadowClone(name="compiler", args=(self.compiler, self.results))
        compiler.start()

        while True:
            if self.state == "off":  # pragma: no cover
                try:
                    logger.debug("Waiting for compiler to join")
                    compiler.join(timeout=10)
                except mp.TimeoutError: # pragma: no cover
                    logger.warning("Compiler failed to join, terminating")
                    compiler.terminate()

                logger.warning("Shutting down")
                break

            if not self.requests.empty():
                event, task = self.requests.get()
                logger.info(f"Request received: ({event}, {task})")

                if event in self.events.keys():
                    logger.info(f"Handling event: {event}")
                    self.events[event]() if event not in ["perform", "wait"] else self.events[event](task)

                else: # pragma: no cover
                    logger.critical(f"Unable to handle event: {event}")
                    continue

                logger.info(f"Successfully handled event: {event}")
                time.sleep(1)

        logger.info("ShadowBot stopped successfully")

    @logger.catch
    def compiler(self):
        """Checks for results in the results queue and stores them in the history
        """

        logger.debug("Running compiler")
        while True:
            if self.state == "off":  # pragma: no cover
                logger.debug("Checking for results before stopping compiler")
                self.compile()
                logger.warning("Stopping compiler")
                break

            self.compile()

    @logger.catch
    def compile(self):
        """Checks for results and puts them into compilation queue
        """

        if not self.results.empty():
            logger.debug("Retrieving results")

            task, result = self.results.get()
            logger.debug(f"{result} compiled for {task}")
            self.history[task] = result

            logger.debug("Putting history into compilation queue")
            self.compilation.put(self.history)

    @logger.catch
    def generate(self):
        """Sends over the result history

        Returns:
            [Dict[str, Optional[Any]]]: Result of every task executed
        """

        logger.info("Sending over result history")

        self.responses.put(self.compilation.get()) if not self.compilation.empty() else logger.warning("Results were not generated")

    @property
    def essence(self):
        """ShadowBot's essence property

        Returns:
            [NamedTuple]: The ShadowBot's name, tasks, and history used to save and load the instance on the network
        """

        return Needle(self.name, self.tasks, self.history)
