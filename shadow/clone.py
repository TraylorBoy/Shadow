"""Task Worker"""

import os
from functools import partial
from typing import Any, Optional

from loguru import logger


class ShadowClone(object):

    """Slave class for perfoming tasks on seperate processes for the ShadowBot instance"""

    def __init__(self, master: object, name: str, task: partial):
        """Initialize the ShadowClone instance

        Args:
            master (object): Master class that delegates tasks and compiles results
            name (str): Name of the signal to execute task
            task (partial): Task to perform
        """

        self._master: object = master
        self._name: str = name
        self._task: partial = task

        logger.debug("Shadow Clone Jutsu")

    @logger.catch
    def perform(self):
        """Performs the assigned task and updates the masters result queue
        """

        logger.debug(f"Performing task: {self._name}")

        result: Optional[Any] = self._task()

        self._master.results.put((self._name, result), block=True)

        logger.debug(f"{self._name} - Result sent to master: {result}")
