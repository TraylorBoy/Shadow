"""Automated task runner"""

import os
from multiprocessing import Process, Queue
from threading import Thread
from typing import Any, Dict, Optional, Tuple

from loguru import logger

from shadow.clone import ShadowClone
from shadow.observer import Observable


class ShadowBot(Observable):

    """Base bot class"""

    def __init__(self):
        """Sets the default properties"""

        # Bot ID
        self.name: Optional[str] = None

        # Task workers
        self.clones: Dict[str, ShadowClone] = {}

        # State
        self.on = False

        # Bot runs on a seperate process
        self.__process: Process = Process(target=self.run)

        # Communication
        self.messages: Queue = Queue()
        self.results: Queue = Queue()

    def setup(self, name: str, tasks: Optional[Dict[str, Tuple[Any]]] = None):
        """Initializes ShadowBot"""

        self.rename(new_name=name)

        if tasks is not None:
            for _signal, _task in tasks.items():
                self.add_task(signal=_signal, task=_task)

    def rename(self, new_name: Optional[str] = None):
        """Name setter"""

        self.name = new_name

    def add_task(
        self, signal: str, task: Tuple[Any]
    ):
        """Delegates task to a ShadowClone which can be called via signal"""

        # Shadow Clone Jutsu
        if not self.check_task(signal=signal):

            clone: ShadowClone = ShadowClone()

            if len(task) > 1:
                # Task came with args
                clone.assign(func=task[0], **task[1])  # type: ignore
            else:
                clone.assign(func=task[0]) # type: ignore

            # Clone performs task when signal is called
            self.clones[signal] = clone

    def remove_task(self, signal: str):
        """Removes clone via the signal it is attached to"""

        if signal in self.clones.keys():
            del self.clones[signal]

    def check_task(self, signal: str):
        """Returns true if there is a task attached to signal"""

        return signal in self.clones.keys()

    def perform_task(self, signal: str, wait: bool = False):
        """Performs the task attached to the signal and returns the result if waited on or returns the task worker to manage the task"""

        result: Optional[Any] = None

        if wait:

            result = self.clones[signal].perform(block=True)
            return result

        else:
            self.clones[signal].perform()

    def get_result(self, signal: str):
        """Waits for the result for the task that was performed"""

        result: Optional[Any] = None

        # Grab last result from clone history if any
        result = self.clones[signal].check(wait=True)

        return result

    def start(self):
        """ShadowBot starts listening for messages on a seperate process"""

        if not self.running():

            # Transition state
            self.on = True

            # Notify observers of state change
            self.notify("Starting up")

            # Run the process
            self.__process.start()

    def stop(self):
        """Stops the running ShadowBot process"""

        if self.running():

            # Send stop message to process
            self.messages.put(("stop", True))

            # Wait for process to finish
            self.__process.join()

    @logger.catch
    def run(self):
        """Waits till it receives a signal then performs task associated with signal"""

        # Notify observers
        self.notify(f"Started running on pid: {os.getpid()}")

        while True:
            if not self.on:
                self.notify("Shutting down")
                break

            # Check if message was received
            if not self.messages.empty():
                # Pass message to handler
                message: Tuple[str, Optional[bool]] = self.messages.get()
                self.__handle_message(message=message)

        self.notify(f"Stopped running on pid: {os.getpid()}")

    @logger.catch
    def __handle_message(self, message: Tuple[str, bool]):
        """Handles messages received from the queue."""

        # Notify observers
        self.notify(f"Message received: {message}")

        signal: str = message[0]
        result: Optional[Any] = None

        if signal == "stop":
            # Transition state to off
            self.on = False

        elif self.check_task(signal=signal):
            # Signal is a task, attempt to perform it
            should_wait: bool = message[1]

            self.notify(f"Performing task: {signal} | Is Blocking: {should_wait}")

            result = self.perform_task(signal=signal, wait=should_wait)

            self.results.put(result) if result is not None else None
            self.notify(f"Compiled result: {result}") if result is not None else None

        else:
            # Do nothing
            pass
