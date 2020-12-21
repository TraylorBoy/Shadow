"""Proxy to the running ShadowBot instance"""

from abc import ABC, abstractmethod

from loguru import logger


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


class ShadowProxy(IShadowProxy, object):

    """Proxy to running ShadowBot instance"""

    def __init__(self, shadowbot: IShadowProxy):
        """Set the ShadowBot instance to connect to

        Args:
            bot (IShadowProxy): Instantiated ShadowBot instance
        """

        self.__bot: IShadowProxy = shadowbot

    @logger.catch
    def perform(self, signal: str):
        """Sends a message to the running ShadowBot process

        Args:
            signal (str): Message to send
        """

        if self.alive():
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
        """Start the ShadowBot instance"""

        with self.__bot as shadowbot:
            shadowbot.keep_alive = True

        return self.alive()

    @logger.catch
    def stop(self):
        """Stop the running ShadowBot instance"""

        with self.__bot as shadowbot:
            shadowbot.keep_alive = False

        return not self.alive()

    def alive(self):
        """Check if the ShadowBot process is alive"""

        return self.__bot.soul.is_alive()
