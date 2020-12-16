"""Worker class that performs tasks on a seperate process"""

import os
import queue

from copy import copy
from threading import Thread
from typing import Any, Callable, Optional, Tuple

from loguru import logger


class ShadowClone:

    """Task worker"""

    def __init__(self):
        """Set initial task"""

        # Keeps track of tasks
        self.task: Optional[Tuple] = None
        self.__thread: Optional[Thread] = None

        # Stores results
        self.history: queue.Queue = queue.Queue()

    @logger.catch
    def __run_task(self):
        """Performs assigned task"""

        logger.debug(f"Running task {self.task} on pid: {os.getpid()}")

        # Run the task and add the result to process queue
        if self.task[1] is not None:
            result: Any = self.task[0](**self.task[1])
        else:
            result: Any = self.task[0]() # pragma: no cover

        # Update result history
        if result is not None:
            logger.debug("Updating history")

            # Store result
            self.history.put(result)

            logger.debug(f"Task finished with result: {result}")

    def clone(self):
        """Prototype method for copying ShadowClones"""

        return copy(self)

    def assign(self, func: Callable, **kwargs):
        """Assigns a new task"""

        # Assign function and function args
        self.task = (func, kwargs)


    def perform(self, block: bool = False):
        """Performs assigned task on a seperate thread, if block then it waits until thread is finished executing"""

        # Create a new thread to run the task on
        # Make it a background thread
        task_d: Thread = Thread(target=self.__run_task, daemon=True)

        # Start the daemon and wait for it if block is set to True
        task_d.start()

        if block:
            logger.debug("Waiting for result")
            task_d.join()

            # Return result
            return self.check()

        else:
            # Store thread and allow ShadowBot to handle it
            self.__thread = task_d

    def check(self, wait: bool = False):
        """Gets result from last completed task"""

        if wait and self.__thread.is_alive():
            logger.debug("Waiting for result")
            self.__thread.join()
            self.__thread = None

        if not self.history.empty():
            return self.history.get()

        logger.debug("No result found")
        return None
