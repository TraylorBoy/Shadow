"""Provides a way to send and receive messages to running ShadowBot process"""

from shadow.bot import ShadowBot
from shadow.observer import ShadowObserver

from abc import abstractmethod

from typing import Any, Dict, Optional, Tuple

class IShadowProxy:

    """Proxy Interface for ShadowBot"""

    @abstractmethod
    def send(self, signal: str, **kwargs):
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
    def observe(self):
        raise NotImplementedError()

class ShadowProxy(IShadowProxy):

    """Proxy to the ShadowBot"""

    def __init__(self):
        """Instantiates ShadowBot"""

        self.bot: ShadowBot = ShadowBot()
        self.observer: Optional[ShadowObserver] = None

    def send(self, signal: str, **kwargs):
        """Sends a signal to the proccess ShadowBot is running on"""

        if self.bot.check_task(signal=signal):
            msg: Tuple[str, Any] = (signal, kwargs)
            self.bot.messages.put(msg)

    def start(self):
        """ShadowBot starts listening for messages on a seperate process"""

        if not self.alive():

            self.notify("Starting up")

            self.bot.soul.start()

    def stop(self):
        """Stops the running ShadowBot process"""

        if self.alive():

            # Send stop message to process
            self.bot.messages.put(("stop", True))

            # Wait for process to finish
            self.bot.soul.join()

    def alive(self):
        """Checks if process is alive"""

        return self.bot.soul.is_alive()

    def observe(self):
        """Creates and registers a ShadowObserver"""

        self.observer = ShadowObserver()

        # Register observer to start receiving notifications
        self.bot.register(observer=self.observer)

    def unobserve(self):
        """Deregisters ShadowObserver from ShadowBot notification list"""

        self.bot.deregister(observer=self.observer)

        self.observer = None
