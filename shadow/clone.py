"""Worker class that performs tasks on a seperate process"""

import os
import queue
from copy import copy
from threading import Lock, Thread
from typing import Any, Callable, List, Optional, Tuple

from loguru import logger


class ShadowClone:

    """Task worker"""

    def __init__(self):
        """Set initial task"""

        # Keeps track of tasks
        self.task: Optional[Tuple] = None
        self.__threads: List[Thread] = []

        # Stores results
        self.history: queue.Queue = queue.Queue()
        self.__hist_lock: Lock = Lock()

    def clone(self):
        """Prototype method for copying ShadowClones"""

        return copy(self)

    def assign(self, func: Callable, **kwargs):
        """Assigns a new task"""

        # Assign function and function args
        self.task = (func, kwargs)

        # Clear threads
        self.clear(all=True)

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

        else:
            # Store thread
            self.__threads.append(task_d)

        # Return result if any
        return self.check()

    @logger.catch
    def __run_task(self):
        """Performs assigned task"""

        logger.debug(f"Running task {self.task} on pid: {os.getpid()}")

        # Run the task and add the result to process queue
        result: Any = self.task[0](**self.task[1])

        # Update result history
        if result is not None:
            # Lock thread for update
            with self.__hist_lock:
                logger.debug("Updating history")

                # Store result
                self.history.put(result)

            logger.debug(f"Task finished with result: {result}")

    def check(self, wait: bool = False):
        """Gets result from last completed task"""

        self.wait() if wait else None

        if not self.history.empty():
            return self.history.get()

        return None

    def unfinished(self):
        """Return number of unfinished tasks"""

        unfinished: int = 0

        if len(self.__threads) > 0:
            for thread in self.__threads:
                if thread.is_alive():
                    unfinished += 1
                else:
                    # Thread finished, remove it
                    self.clear(t=thread)  # pragma: no cover

        return unfinished

    def wait(self):
        """Waits for unfinished tasks to complete"""

        if self.unfinished() > 0:
            for thread in self.__threads:
                if thread.is_alive():
                    # Wait for it to finish executing
                    logger.debug("Waiting for thread to finish")
                    thread.join()
                    self.clear(t=thread)

            return True

        return False

    def clear(self, t: Optional[Thread] = None, all: bool = False):
        """Clears one or all threads in thread list that were not waited on"""

        if all:
            self.__threads = []
            return True
        elif t in self.__threads:
            for i in range(len(self.__threads)):
                if t is self.__threads[i]:
                    logger.debug("Deleting thread")
                    del self.__threads[i]

        return False
