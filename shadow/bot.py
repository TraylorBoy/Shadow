"""Task Manager"""

import time
import multiprocessing as mp

from threading import Thread

from functools import partial

from typing import Dict, Any, Optional, Callable, Tuple, List

from shadow.clone import ShadowClone
from shadow.interface import IShadowBot

from loguru import logger

class ShadowBot(IShadowBot):

    """Master class for running tasks performed by ShadowClones (slaves)"""

    def __repr__(self):
        name: str = self.id
        tasks: str = list(self.clones.keys())
        state: str = "Running" if self.alive() else "Dead"
        current_tasks: List[str] = []

        if state == "Running":
            for task, clone in self.clones.items():
                if clone.alive():
                    current_tasks.append(task)

        return f"""
            {name}: {state}
            ---------------
            Tasks - {tasks}
            Running - {current_tasks if len(current_tasks) > 0 else 'None'}
        """

    def __init__(self, name: str, tasks: Dict[str, partial]):
        """Sets ShadowBot's default properties and state

        Args:
            name (str): Name to identify the ShadowBot on the network
            tasks (Dict[str, partial]): Tasks for the ShadowBot to perform
        """

        self.id: str = name
        self.on: bool = False
        self.manager: Dict[str, partial] = tasks

        self.setup()

    def __shadow_clone_jutsu(self, task: str):
        """Wraps the ShadowClone's perform method to run in a seperate Thread

        Args:
            task (str): Task to be executed
        """

        logger.info("~Shadow Clone Jutsu~")

        self.clones[task]["soul"] = Thread(target=self.clones[task]["clone"].perform, name=task)

        self.clones[task]["soul"].start()

    def __kill(self):
        """Transitions state from on to off"""

        logger.warning("Shutting down")

        self.on = False

    def setup(self):
        """Instantiates the ShadowBot's process, message queues, event factory, and task workers (ShadowClones)
        """

        logger.debug("Setting up")

        self.soul: mp.Process = mp.Process(target=self.core, daemon=True)

        self.results: mp.Queue = mp.Queue()
        self.tasks: mp.Queue = mp.Queue()
        self.compile: mp.Queue = mp.Queue()

        self.requests: mp.Queue = mp.Queue()
        self.responses: mp.Queue = mp.Queue()

        # Delegate tasks
        self.clones: Dict[str, Dict[str, Optional[Any]]] = {}

        for signal, task in self.manager.items():
            self.clones[signal] = {
                "clone": ShadowClone(pipe=self.results, task=task),
                "soul": None
            }

    def alive(self):
        """Checks if ShadowBot process has started

        Returns:
            [bool]: Process is running or not
        """
        return self.soul.is_alive()

    def start(self):
        """Transitions state from off to on and starts the ShadowBot's process"""

        if self.alive():
            logger.warning("Already running")
            return None

        logger.info("Starting up")

        self.on = True

        try:

            self.soul.start()

        except AssertionError:
            # Process has been used previously, set a new one
            self.restart()

    def stop(self):
        """Stop the running ShadowBot process"""

        if self.alive():
            logger.info("Stopping")

            # Send a kill signal
            self.requests.put("stop", block=True)
            self.soul.join()

    def restart(self):
        """Re-instantiates the ShadowBot's process"""

        logger.info("Restarting")

        self.__init__(name=self.id, tasks=self.manager)

        self.start()

    def perform(self):
        """Performs task retrieved from the task queue

        Args:
            task (str): Task to be executed
        """

        if not self.tasks.empty():
            task: str = self.tasks.get(block=True)

            if task not in self.clones.keys():
                logger.warning(f"Invalid task received: {task}")
                return None

            logger.info(f"Performing task: {task}")

            # Create and start the shadowclone's thread
            self.__shadow_clone_jutsu(task)

    def wait(self):
        """Waits for ShadowClone to finish performing the task
        """

        if not self.compile.empty():
            task: str = self.compile.get(block=True)

            if task not in self.clones.keys():
                logger.warning(f"Invalid task received: {task}")
                return None

            if self.clones[task]["soul"] is not None and self.clones[task]["soul"].is_alive():

                logger.info(f"Waiting for {task} to complete")
                self.clones[task]["soul"].join()

    @logger.catch
    def core(self):
        """Method is called when the process is started"""

        while self.on:
            if not self.on:  # pragma: no cover
                logger.warning("Terminating process")
                break

            if not self.requests.empty():

                requests: Dict[str, Callable] = {
                    "stop": self.__kill,
                    "perform": self.perform,
                    "wait": self.wait
                }

                request: str = self.requests.get(block=True)

                logger.info(f"Request received: {request}")

                if request in requests.keys():
                    requests[request]()

            time.sleep(1)

    @logger.catch
    def request(self, type: str, task: Optional[str]):
        """Sends a request to the ShadowBot

        Args:
            type (str): Type of request to send
            task (Optional[str]): Task to send to the ShadowBot if the request type is "wait" or "perform"
        """

        if self.alive():
            logger.info(f"Sending request: {type} - {task}")

            # Either perform or wait for the result
            self.tasks.put(task, block=True) if type == "perform" else self.compile.put(task, block=True)
            self.requests.put(type, block=True)

            time.sleep(1)

    @logger.catch
    def response(self):
        """Check for a response from the ShadowBot

        Returns:
            [Optional[Tuple[str, any]]]: Result from the requested task
        """

        if not self.results.empty():
            response: Tuple[str, Any] = self.results.get(block=True)

            logger.info(f"Result compiled, sending response: {response}")

            return response

