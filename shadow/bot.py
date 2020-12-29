"""Task Manager"""

import multiprocessing as mp
from threading import Thread

from functools import partial

from typing import Dict, Any, Optional, Callable, Tuple, List

from shadow.clone import ShadowClone
from shadow.interface import IShadowBot

from loguru import logger

# TODO - Run ShadowClone listeners on startup for core method


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
        self.tasks: Dict[str, partial] = tasks

        self.setup(tasks)

    def setup(self, tasks: Dict[str, partial]):
        """Instantiates the ShadowBot's process, message queues, event factory, and task workers (ShadowClones)

        Args:
            tasks (Dict[str, partial]): Tasks to delegate to the ShadowClones
        """

        logger.debug("Setting up")

        self.soul: mp.Process = mp.Process(target=self.core)

        self.pipe: Dict[str, mp.Queue] = {
            "task": mp.Queue(),
            "wait": mp.Queue(),
            "result": mp.Queue(),
            "event": mp.Queue(),
            "response": mp.Queue(),
            "compile": mp.Queue(),
        }

        self.events: Dict[str, Callable] = {
            "kill": self.stop,
            "task": self.perform,
            "get": self.get,
            "wait": self.wait,
        }

        # Delegate tasks
        self.clones: Dict[str, Dict[str, Optional[Any]]] = {}

        for signal, task in tasks.items():
            self.clones[signal] = ShadowClone(
                id=signal, pipe=self.pipe["result"], task=task
            )

    def shadow_clone_jutsu(self, task: str):
        """Wraps the ShadowClone's perform method to run in a seperate Thread

        Args:
            task (str): Task to be executed

        Returns:
            [Thread]: Threaded ShadowClone instance
        """

        logger.info("~Shadow Clone Jutsu~")

        if task in self.clones.keys():

            shadowclone: Thread = Thread(target=self.clones[task].perform, name=task)

            return shadowclone

    def perform(self):
        """Performs task retrieved from the task queue

        Returns:
            [bool]: Task is being performed
        """

        if not self.pipe["task"].empty():

            task: str = self.pipe["task"].get(block=True)

            logger.debug(f"Performing task: {task}")

            # Create the shadowclone's thread
            self.shadow_clone_jutsu(task).start()

    def alive(self):
        """Checks if ShadowBot's process is running

        Returns:
            [bool]: Process is alive or not
        """

        return self.soul.is_alive()

    def kill(self):
        """Stop the running ShadowBot process"""

        if self.alive():
            logger.info("Sending kill signal to ShadowBot")

            # Warn of zombie clones
            for task, clone in self.clones.items():
                if clone.alive():
                    logger.warning(
                        f"{task} is unfinshed, {clone} still alive"
                    )  # pragma: no cover

            # Send a kill signal
            self.pipe["event"].put("kill", block=True)

            self.soul.join()

    def stop(self):
        """Transitions state from on to off"""

        logger.warning("Shutting down")

        self.on = False

    def start(self):
        """Transitions state from off to on and starts the ShadowBot's process"""

        logger.info("Starting up")

        self.on = True

        if not self.alive():

            try:

                self.soul.start()

            except AssertionError:
                raise AssertionError

    def wait(self):
        """Waits for ShadowClone to finish performing the task sent to the wait pipe"""

        if not self.pipe["wait"].empty():
            wait_for: str = self.pipe["wait"].get(block=True)

            for task, clone in self.clones.items():

                if wait_for == task:
                    logger.info(f"Waiting for {wait_for} to complete")

                    if clone.alive():
                        clone.wait()

                    logger.info("Task complete")

    def get(self):
        """Retrieves result form pipe and sends it to the response pipe

        Returns:
            [bool]: Did retrieve result from pipe
        """

        if not self.pipe["result"].empty():

            response: Tuple[str, Any] = self.pipe["result"].get(block=True)

            logger.info(f"Received result: {response}")

            self.pipe["response"].put(response, block=True)

            logger.debug("Result redirected to response pipe")

            return True

        return False

    def compile(self):
        """Waits for task to complete and routes the result to the response pipe"""

        if not self.pipe["compile"].empty():

            task: str = self.pipe["compile"].get(block=True)

            logger.info(f"Compiling: {task}")

            self.pipe["wait"].put(task, block=True)
            self.wait()

            result_compiled: bool = self.get()

            if result_compiled:
                if not self.pipe["response"].empty():
                    # Retrieve the name of the task completed and its result
                    task_name, result = self.pipe["response"].get()

                    logger.success(f"{task_name} finished with result: {result}")

                    return (task_name, result)

            logger.warning(f"Failed to compile {task}")

            return None

    def listen(self):
        """Retrieves event from event pipe and handles it

        Returns:
            [bool]: Event retrieved and successfully handled
        """

        if not self.pipe["event"].empty():
            event: str = self.pipe["event"].get(block=True)

            logger.info(f"Event received: {event}")

            if event in self.events.keys():

                logger.info("Handling event")

                self.events[event]()

                return True

        return False

    def reset(self):
        """Re-instantiates the ShadowBot's process"""

        logger.debug(f"Resetting soul: {self.soul}")

        self.__init__(name=self.id, tasks=self.tasks)

        logger.debug(f"Soul reset: {self.soul}")

    @logger.catch
    def core(self):
        """Method is called when the process is started"""

        while self.on:
            if not self.on:  # pragma: no cover
                logger.warning("Terminating process")
                break

            # Listen for events
            if self.listen():
                logger.info("Event handled")
