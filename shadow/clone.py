"""Worker class that performs tasks on a seperate process"""

from copy import copy
from multiprocessing import Process, Queue
from typing import Any, Callable, Optional, Tuple

from loguru import logger


class ShadowClone:

    """Task worker"""

    def __init__(self):
        """Set initial task"""

        self.task: Optional[Tuple] = None

        # Results from completed task
        self.__result: Queue = Queue()

    def clone(self):
        """Prototype method for copying ShadowClones"""

        return copy(self)

    def assign(self, func: Callable, **kwargs):
        """Assigns a new task"""

        # Assign function and function args
        self.task = (func, kwargs)

        logger.debug(f"New task assigned: {self.task}")

    def perform(self, block: bool = False):
        """Performs assigned task on a seperate process, if block then it waits until process is finished executing"""

        # Create a new process to run the task on
        task_process: Process = Process(target=self.__run_task)

        # Start the process and wait for it if block is set to True
        task_process.start()

        if block:
            logger.debug("Waiting for result")
            task_process.join()

        # Return result if any
        if not self.__result.empty():
            return self.__result.get()

    def __run_task(self):
        """Performs assigned task"""

        logger.debug(f"Running task {self.task}")

        # Run the task and add the result to process queue
        result: Any = self.task[0](**self.task[1])

        if result is not None:
            self.__result.put(result)

        logger.debug(f"Task finished with result: {self.__result}")
