"""Automated task runner"""

import os
from multiprocessing import Process, Queue
from typing import Any, Dict, Optional, Tuple

from loguru import logger

from shadow.clone import ShadowClone
from shadow.observer import Observable


class ShadowBot(Observable):

    """Base bot class"""

    def __init__(self):
        """Set the initial state and properties of the bot"""

        # Bot ID
        self.name: Optional[str] = None

        # Task workers
        self.clones: Dict[str, ShadowClone] = {}

        # Bot runs on a seperate process
        self.soul: Process = Process(target=self.__run)

        # Communication
        self.messages: Queue = Queue()
        self.results: Queue = Queue()

    @logger.catch
    def __run(self):
        """Waits till it receives a signal then performs task associated with signal"""

        self.notify(f"Started running on pid: {os.getpid()}")

        while True:
            if not self.messages.empty():

                message: Tuple[str, Optional[bool]] = self.messages.get()

                if message[0] == "stop":  # pragma: no cover
                    self.notify("Shutting down")
                    break

                elif message[0] == "result":
                    result: Optional[Any] = self.get_result(signal=message[1])
                    self.results.put(result) if result is not None else None

                elif self.check_task(signal=message[0]):
                    if message[1]:
                        # Task is blocking
                        # Wait for result
                        result: Optional[Any] = self.perform_task(
                            signal=message[0], wait=True
                        )
                        self.results.put(result) if result is not None else None
                    else:
                        self.perform_task(signal=message[0])
                else:
                    self.notify("Invalid message received")

        self.notify(f"Stopped running on pid: {os.getpid()}")

    def add_task(self, signal: str, task: Tuple[Any]):
        """Delegates task to a ShadowClone which can be called via signal

        Args:
            signal (str): Signal that will be called in order to run task
            task (Tuple[Any]): Task to be executed when signal is received
        """

        # Shadow Clone Jutsu
        if not self.check_task(signal=signal):

            clone: ShadowClone = ShadowClone()

            if len(task) > 1:
                # Task came with args
                clone.assign(func=task[0], **task[1])  # type: ignore
            else:
                clone.assign(func=task[0])  # type: ignore

            # Clone performs task when signal is called
            self.clones[signal] = clone

    def remove_task(self, signal: str):
        """Removes clone via the signal it is attached to

        Args:
            signal (str): Signal that will be called in order to run task
        """

        if signal in self.clones.keys():
            del self.clones[signal]

    def check_task(self, signal: str):
        """Returns true if there is a task attached to signal

        Args:
            signal (str): Signal that will be called in order to run task

        Returns:
            [type]: [description]
        """

        return signal in self.clones.keys()

    def perform_task(self, signal: str, wait: bool = False):
        """Performs the task attached to the signal and returns the result if waited on or returns the task worker to manage the task

        Args:
            signal (str): Signal that will be called in order to run task
            wait (bool, optional): Wait for task to finish executing before continuing. Defaults to False.

        Returns:
            [Any]: Result if wait was set to True and task returns a result that is not None
        """

        if wait:
            return self.clones[signal].perform(block=True)

        else:
            self.clones[signal].perform()

    def get_result(self, signal: str):
        """Waits for the result for the task that was performed

        Args:
            signal (str): Signal that will be called in order to run task

        Returns:
            [Any]: Result if wait was set to True and task returns a result that is not None
        """

        if self.check_task(signal=signal):
            # Grab last result from clone history if any
            return self.clones[signal].check(wait=True)
