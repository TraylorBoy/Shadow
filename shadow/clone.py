"""Task worker"""

import os

from threading import Thread, current_thread

from functools import partial

from typing import Optional, Any

from shadow.interface import IShadowBot

from loguru import logger

class ShadowClone(IShadowBot):

    """Slave class for perfoming tasks on seperate threads for the ShadowBot instance"""

    def __init__(self, id: str, pipe: Any, task: partial):
        """Initializes the task worker instance

        Args:
            pipe (Any): The Queue object ShadowClone should put the result in after completing the assigned task
            task (partial): Task for ShadowClone to perform
        """

        self.pipe: Any = pipe
        self.task: partial = task
        self.name: str = id
        self.soul: Optional[Thread] = None

    def perform(self):
        """Calls assigned task and puts the result in the pipe set during initialization
        """

        self.soul = current_thread()

        logger.debug(f"Performing task: {self.task}")
        logger.debug(f"Master PID: {os.getppid()} {self.name} PID: {os.getpid()}")

        try:

            result: Optional[Any] = self.task()

            self.pipe.put((self.name, result), block=True)

            logger.debug(f"Completed task, result: {result}")

        except Exception as e: # pragma: no cover

            logger.warning(f"Error occured while performing task: {self.master} - {self.name} - {self.task}")
            logger.exception(e)

    def alive(self):
        """Checks if ShadowClone's thread is alive

        Returns:
            [bool]: ShadowClone's thread is alive
        """

        if self.soul is not None:
            return self.soul.is_alive()

        else:
            return False

    def wait(self):
        """Waits for the ShadowClone to finish the assigned task

        Returns:
            [bool]: Task was waited on
        """

        if self.alive():

            logger.debug("Sending result")

            self.soul.join(timeout=1)

            if not self.alive():

                logger.debug("Result sent")

                return True

        return False

