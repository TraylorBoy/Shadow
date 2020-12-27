"""Interfaces for the Shadow package"""

from typing import Dict

from functools import partial

from abc import ABC, abstractmethod

class IShadowNetwork(ABC):

    """ShadowNetwork Interface"""

    @abstractmethod
    def serve(self):
        raise NotImplementedError()

    @abstractmethod
    def send(self, message: str):
        raise NotImplementedError()

    @abstractmethod
    def kill(self):
        raise NotImplementedError()

    @abstractmethod
    def build(self, name:str, tasks: Dict[str, partial]):
        raise NotImplementedError()

class IShadowBot(ABC):

    """ShadowBot Interface"""

    @abstractmethod
    def perform(self):
        raise NotImplementedError()

    @abstractmethod
    def alive(self):
        raise NotImplementedError()

    @abstractmethod
    def wait(self):
        raise NotImplementedError()
