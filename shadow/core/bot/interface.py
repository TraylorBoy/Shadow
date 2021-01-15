"""Interfaces for the Shadow package"""

from typing import Optional

from abc import ABC, abstractmethod

class IShadowBot(ABC):

    """ShadowBot Interface"""

    @abstractmethod
    def request(self, event: str, task: Optional[str]):
        raise NotImplementedError()

    @abstractmethod
    def response(self, task: str):
        raise NotImplementedError()

    @abstractmethod
    def alive(self):
        raise NotImplementedError()

    @abstractmethod
    def perform(self, task: str):
        raise NotImplementedError()

    @abstractmethod
    def wait(self, task: str):
        raise NotImplementedError()

    @abstractmethod
    def jutsu(self, task: str):
        raise NotImplementedError()

    @abstractmethod
    def kill(self):
        raise NotImplementedError()
