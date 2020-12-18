"""Publish-Subscriber classes used for observing a ShadowBot"""

from typing import List

from loguru import logger


class ShadowObserver:

    """Subscriber class"""

    def update(self, *args, **kwargs):
        """Notifies all registered observers"""

        for msg in args:
            logger.info(msg)

        for key, msg in kwargs.items():
            logger.info(f"{key}: {msg}")

    def debug(self, *args, **kwargs):
        """Notifies all registered observers of a debug message"""

        for msg in args:
            logger.debug(msg)

        for key, msg in kwargs.items():
            logger.debug(f"{key}: {msg}")


class Observable:

    """Publisher class"""

    observers: List[ShadowObserver] = []

    def register(self, observer: ShadowObserver):
        """Adds observer to observer list

        Args:
            observer (ShadowObserver): Observer to add to observer list
        """

        if observer not in self.observers:  # pragma: no cover
            self.observers.append(observer)

    def deregister(self, observer: ShadowObserver):
        """Removes observer from observer list

        Args:
            observer (ShadowObserver): Observer to remove from observer list
        """

        if observer in self.observers:  # pragma: no cover
            self.observers.remove(observer)

    def notify(self, *args, **kwargs):
        """Sends a notification to all registered observers"""

        for observer in self.observers:
            observer.update(*args, **kwargs)

    def bug(self, *args, **kwargs):
        """Sends a debug message to all registered observers"""

        for observer in self.observers:
            observer.debug(*args, **kwargs)
