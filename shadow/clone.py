"""Task Worker"""

import os
from functools import partial
from threading import Lock
from typing import Any, Optional

from loguru import logger


class ShadowClone(object):

    """Slave class for perfoming tasks on seperate threads for the ShadowBot instance"""

    def __init__(self, master: object, name: str, task: partial):
        # Todo: Docstring

        self._master: object = master
        self._name: str = name
        self._task: partial = task

    @logger.catch
    def perform(self):
        # Todo: Docstring

        self._master.bug(
            f"Performing task: {self._name} - {self._task} on pid: {os.getpid()}"
        )

        result: Optional[Any] = self._task()

        with Lock():
            self._master.bug(f"{self._name} - Sending result to master")
            self._master.results.put((self._name, result))

        self._master.bug(f"{self._name} - Result sent to master: {result}")
