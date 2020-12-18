"""Provides a way to send and receive messages to running ShadowBot process"""

from abc import abstractmethod
from typing import Any, Optional, Tuple

from shadow.bot import ShadowBot
from shadow.observer import ShadowObserver


class IShadowProxy:

    """Proxy Interface for ShadowBot"""

    @abstractmethod
    def send(self, signal: str, wait: bool = False):
        raise NotImplementedError()

    @abstractmethod
    def start(self):
        raise NotImplementedError()

    @abstractmethod
    def stop(self):
        raise NotImplementedError()

    @abstractmethod
    def alive(self):
        raise NotImplementedError()

    @abstractmethod
    def observe(self):
        raise NotImplementedError()

    @abstractmethod
    def unobserve(self):
        raise NotImplementedError()


class ShadowProxy(IShadowProxy):

    """Proxy to the ShadowBot"""

    def __init__(self):
        """Instantiates a new ShadowBot object"""

        self.bot: ShadowBot = ShadowBot()
        self.observer: Optional[ShadowObserver] = None

    def send(self, signal: str, wait: bool = False):
        """Sends a signal to the proccess ShadowBot is running on

        Args:
            signal (str): Signal that will be called in order to run task
            wait (bool, optional): Wait for task to finish executing before continuing. Defaults to False.

        Returns:
            [Any]: Result if wait was set to True and task returns a result that is not None
        """

        if self.bot.check_task(signal=signal):
            msg: Tuple[str, Any] = (signal, wait)
            self.bot.messages.put(msg)

            if wait:
                result: Any = self.bot.results.get()
                return result

    def wait(self, signal: str):
        """Waits for task to finish and returns the result

        Args:
            signal (str): Signal that will be called in order to run task

        Returns:
            [Any]: Result if wait was set to True and task returns a result that is not None
        """

        result: Optional[Any] = None

        if self.bot.check_task(signal=signal):
            msg: Tuple[str, str] = ("result", signal)
            self.bot.messages.put(msg)

            result = self.bot.results.get()

        return result

    def start(self):
        """ShadowBot starts listening for messages on a seperate process"""

        if not self.alive():

            self.bot.notify("Starting up")

            self.bot.soul.start()

    def stop(self):
        """Stops the running ShadowBot process by sending it the stop signal"""

        if self.alive():

            # Send stop message to process
            self.bot.messages.put(("stop", True))

            # Wait for process to finish
            self.bot.soul.join()

    def alive(self):
        """Checks if ShadowBot process is running

        Returns:
            [bool]: If ShadowBot process is running or not
        """

        return self.bot.soul.is_alive()

    def observe(self):
        """Creates and registers a ShadowObserver for the proxy object"""

        self.observer = ShadowObserver()

        # Register observer to start receiving notifications
        self.bot.register(observer=self.observer)

    def unobserve(self):
        """Deregisters the proxy object's ShadowObserver"""

        self.bot.deregister(observer=self.observer)

        self.observer = None
