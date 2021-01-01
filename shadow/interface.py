"""Interfaces for the Shadow package"""

from typing import Dict, Optional

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
    def sew(self, name: str, tasks: Dict[str, partial]):
        raise NotImplementedError()

    @abstractmethod
    def retract(self, name: str):
        raise NotImplementedError()

    @abstractmethod
    def signal(self, name: str, event: str, task: str):
        raise NotImplementedError()


class IShadowBot(ABC):

    """ShadowBot Interface"""

    @abstractmethod
    def request(self, type: str, task: Optional[str]):
        raise NotImplementedError()

    @abstractmethod
    def response(self):
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
