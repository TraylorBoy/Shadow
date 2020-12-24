"""Proxy to the running ShadowBot instance"""

import os
from abc import ABC, abstractmethod

from loguru import logger

from shadow.observer import ShadowObserver


class IShadowProxy(ABC):

    """Interface for the ShadowProxy class"""

    @abstractmethod
    def perform(self, signal: str):
        raise NotImplementedError()

    @abstractmethod
    def wait(self, signal: str):
        raise NotImplementedError()

    @abstractmethod
    def compile(self, signal: str):
        raise NotImplementedError()

    @abstractmethod
    def start(self):
        raise NotImplementedError()

    @abstractmethod
    def stop(self):
        raise NotImplementedError()

    @abstractmethod
    def kill(self):
        raise NotImplementedError()

    @abstractmethod
    def daemonize(self):
        raise NotImplementedError()


class ShadowProxy(IShadowProxy, object):

    """Proxy to running ShadowBot instance"""

    def __init__(self, shadowbot: IShadowProxy):
        """Set the ShadowBot instance to connect to

        Args:
            bot (IShadowProxy): Instantiated ShadowBot instance
        """

        self.__bot: IShadowProxy = shadowbot
        self.__observer: ShadowObserver = ShadowObserver()
        self.__pid: str = "0"

        # Check if ShadowBot is already running as a daemon
        if os.path.exists(f"shadow/data/daemons/{self.__bot.id}.pid"):  # type: ignore
            with open(f"shadow/data/daemons/{self.__bot.id}.pid", "r") as daemon:  # type: ignore

                pid = daemon.read()

                if pid is not None:
                    self.__pid = pid

        self.__daemonized: bool = self.__pid != "0"

    @logger.catch
    def perform(self, signal: str):
        """Sends a message to the running ShadowBot process

        Args:
            signal (str): Message to send
        """

        if self.alive() and signal in self.__bot.clones.keys():
            self.__bot.requests.put(signal)  # type: ignore

    @logger.catch
    def wait(self, signal: str):
        """Waits for tasks to complete

        Args:
            signal (str): Signal used to call task

        Returns:
            [Any]: Result from completed task
        """

        if self.alive():

            self.__bot.wait(signal=signal)

            return self.__bot.responses.get(block=True)  # type: ignore

    @logger.catch
    def compile(self, signal: str):
        """Perform signal and wait for result

        Args:
            signal (str): Signal used to call the task
            run (bool, optional): Run the task associated with the signal. Defaults to False.
        """

        if self.alive():
            self.perform(signal=signal)

            return self.wait(signal=signal)

    @logger.catch
    def start(self):
        """Start the ShadowBot instance

        Returns:
            [bool]: ShadowBot successfully started
        """

        with self.__bot as shadowbot:
            shadowbot.keep_alive = True

        return self.alive()

    @logger.catch
    def stop(self):
        """Stop the running ShadowBot instance

        Returns:
            [bool]: ShadowBot successfully started
        """

        with self.__bot as shadowbot:
            shadowbot.keep_alive = False

        return not self.alive()

    @logger.catch
    def daemonize(self):  # pragma: no cover
        """Run ShadowBot as a background process"""

        self.__bot.daemonize()

    @logger.catch
    def kill(self):  # pragma: no cover
        """Stop ShadowBot daemon process"""

        self.__bot.kill()

    def is_daemon(self):  # pragma: no cover
        """Checks if ShadowBot process is running as a daemon"""

        return self.__daemonized

    def alive(self):
        """Check if the ShadowBot process is alive"""

        return self.__bot.soul.is_alive()

    def observe(self):
        """Registers proxy observer to the ShadowBot instance"""

        self.__bot.register(observer=self.__observer)

    def unobserve(self):
        """Unregisters proxy observer from the ShadowBot instance"""

        self.__bot.deregister(observer=self.__observer)

    def list_signals(self):
        """Returns a list of all signals attached to the ShadowBot instance
        """

        return list(self.__bot.clones.keys())
