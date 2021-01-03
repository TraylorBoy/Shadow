"""Task worker"""

import os

from threading import Thread, current_thread

from functools import partial

from typing import Optional, Any

from loguru import logger


class ShadowClone(object):

    """Slave class for perfoming tasks on seperate threads for the ShadowBot instance"""

    def __init__(self, pipe: Any, task: partial):
        """Initializes the task worker instance

        Args:
            pipe (Any): The Queue object ShadowClone should put the result in after completing the assigned task
            task (partial): Task for ShadowClone to perform
        """

        self.pipe: Any = pipe
        self.task: partial = task
        self.soul: Optional[Thread] = None

    def perform(self):
        """Calls assigned task and puts the result in the pipe set during initialization"""

        self.soul = current_thread()

        logger.debug(f"Performing task: {self.task}")
        logger.debug(f"Master PID: {os.getppid()} {self.soul.name} PID: {os.getpid()}")

        try:

            result: Optional[Any] = self.task()

            self.pipe.put((self.soul.name, result), block=True)

            logger.debug(f"Completed task, result: {result}")

        except Exception as e:  # pragma: no cover

            logger.warning(
                f"Error occured while performing task: {self.soul.name} - {self.task}"
            )

            logger.exception(e)

            self.pipe.put((self.soul.name, e))


