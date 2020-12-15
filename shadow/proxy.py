"""Provides a way to send and receive messages to running ShadowBot process"""

from shadow.bot import ShadowBot
from shadow.observer import ShadowObserver

from abc import abstractmethod

from typing import Any, Dict, Optional, Tuple

class IShadowProxy:

    """Proxy Interface for ShadowBot"""

    # Todo - Move to core
    @abstractmethod
    def setup(self, name: str, tasks: Optional[Dict[str, Tuple[Any]]] = None):
        raise NotImplementedError()

    # Todo - Edit ShadowBot tasks (add, remove) &  move to core
    @abstractmethod
    def edit(self, signal: str, remove: bool = False, add: bool = True, task: Optional[Tuple[Any]] = None):
        raise NotImplementedError()

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


    # Todo - Move to core
    def setup(self, name: str, tasks: Optional[Dict[str, Tuple[Any]]] = None):
        """Sets ShadowBot properties and tasks"""

        self.bot.name = name

        if tasks is not None:
            for _signal, _task in tasks.items():
                self.bot.add_task(signal=_signal, task=_task)

    # Todo - Edit ShadowBot tasks (add, remove) &  move to core
    def edit(self, signal: str, remove: bool = False, add: bool = False, task: Optional[Tuple[Any]] = None):
        """Delegates task to a ShadowClone which can be called via signal"""
        raise NotImplementedError()

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
