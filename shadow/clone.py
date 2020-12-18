"""Worker class that performs tasks on a seperate process"""

import os
import queue
from copy import copy
from threading import Lock, Thread
from typing import Any, Callable, Optional, Tuple

from loguru import logger


class ShadowClone:

    """Task worker"""

    def __init__(self):
        """Set initial state and properties"""

        # Keeps track of tasks
        self.task: Optional[Tuple] = None
        self.__thread: Optional[Thread] = None
        self.__thread_lock: Lock = Lock()

        # Stores results
        self.history: queue.Queue = queue.Queue()

    @logger.catch
    def __run_task(self):
        """Method runs on a seperate thread performing assigned task"""

        logger.debug(f"Running task {self.task} on pid: {os.getpid()}")

        # Run the task and add the result to process queue
        if self.task[1] is not None:
            result: Any = self.task[0](**self.task[1])
        else:
            result: Any = self.task[0]()  # pragma: no cover

        # Update result history
        if result is not None:
            with self.__thread_lock:
                logger.debug("Updating history")

                # Store result
                self.history.put(result)

            logger.debug(f"Task finished with result: {result}")

    def clone(self):
        """Prototype method for copying ShadowClones

        Returns:
            [ShadowClone]: Copy of the instansiated ShadowClone object
        """

        return copy(self)

    def assign(self, func: Callable, **kwargs):
        """Assigns a new task to the ShadowClone

        Args:
            func (Callable): Task to assign
        """

        # Assign function and function args
        self.task = (func, kwargs)

    def perform(self, block: bool = False):
        """Performs assigned task on a seperate thread

        Args:
            block (bool, optional): Waits until thread is finished executing if set to True. Defaults to False.

        Returns:
            [Any]: Result if block was set to True and task returns a result that is not None
        """

        # Create a new thread to run the task on
        # Make it a background thread
        task_d: Thread = Thread(target=self.__run_task, daemon=True)

        # Start the daemon and wait for it to finish if block is set to True
        task_d.start()

        if block:
            logger.debug("Waiting for result")
            task_d.join()

            result: Optional[Any] = self.check()

            if result is not None:
                return result

        else:
            # Store thread and allow ShadowBot to handle it
            self.__thread = task_d

    def check(self, wait: bool = False):
        """Gets result from last completed task

        Args:
            wait (bool, optional): Waits for current task to complete. Defaults to False.

        Returns:
            [Any]: Result of task completed if result is not None
        """

        if wait and self.__thread is not None and self.__thread.is_alive():
            logger.debug("Waiting for result")
            self.__thread.join()

        if self.__thread is not None and not self.__thread.is_alive():
            self.__thread = None

        if not self.history.empty():
            logger.debug("Result found")
            return self.history.get()

        logger.debug("No result found")
