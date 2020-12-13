"""Automated task runner"""

import os
from multiprocessing import Process, Queue
from typing import Any, Callable, Dict, Optional, Tuple

from loguru import logger

from shadow.clone import ShadowClone
from shadow.observer import Observable


class ShadowBot(Observable):

    """Base bot class"""

    def __init__(self):
        """Sets the default properties"""

        self.__setup()

        self.__process: Process = Process(target=self.run)
        self.messages: Queue = Queue()
        self.results: Queue = Queue()

    def __setup(self):
        """Initializes ShadowBot"""

        # Bot ID
        self.name: Optional[str] = None

        # Create task workers and add default tasks
        self.__shadow_clone_jutsu()

        # State
        self.on = False

    def __shadow_clone_jutsu(self):
        """Creates worker dict and instantiates initial workers"""

        self.clones: Dict[str, ShadowClone] = {}
        self.add_task(signal="history", task=self.history)

    def rename(self, new_name: Optional[str] = None):
        """Name setter"""

        self.name = new_name

    def running(self):
        """Checks if process is started and state is on"""

        turned_on: bool = self.on and self.__process.is_alive()

        return turned_on

    def add_task(
        self, signal: str, task: Callable, task_args: Optional[Dict[str, Any]] = {}
    ):
        """Delegates task to a ShadowClone which can be called via signal"""

        # Shadow Clone Jutsu
        if signal not in self.clones.keys():
            # Create a clone and assign the task
            clone: ShadowClone = ShadowClone()

            clone.assign(func=task, **task_args)  # type: ignore

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
        """Performs the task attached to the signal and returns the result"""

        shadowclone: ShadowClone = self.clones[signal]

        result: Optional[Any] = None

        result = shadowclone.perform(block=True) if wait else shadowclone.perform()

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

    def history(self):
        """Retrieves all results from each clone history"""

        hist: Dict[str, Optional[Any]] = {}
        skip_list = ["history"]

        for signal, clone in self.clones.items():
            if signal in skip_list:
                continue

            hist[signal] = clone.check()

        return hist

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
