"""Singleton pattern helper class"""

#https://github.com/faif/python-patterns/blob/master/patterns/creational/borg.py

from typing import Dict, Any

class Borg:

    """Subclasses share state between each instance"""

    _shared_state: Dict[Any, Any] = {}

    def __init__(self):
        """Initializes each instance with the shared state

        Args:
            key (str): Key for storing and retrieving the shared state in cache file
        """

        self.__dict__ = self._shared_state

