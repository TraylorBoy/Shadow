"""Interfaces for the Shadow package"""

from functools import partial
from typing import Optional, Tuple, Any, Dict

from abc import ABC, abstractmethod


class IShadowNetwork(ABC):

    """ShadowNetwork Interface"""

    @abstractmethod
    def serve(self):
        raise NotImplementedError()

    @abstractmethod
    def kill(self):
        raise NotImplementedError()

    @abstractmethod
    def send(self, message: Tuple[str, Optional[Any]]):
        raise NotImplementedError()

    @abstractmethod
    def alive(self):
        raise NotImplementedError()

    @abstractmethod
    def status(self):
        raise NotImplementedError()

class IShadowBot(ABC):

    """ShadowBot Interface"""

    @abstractmethod
    def request(self, event: str, task: Optional[str]):
        raise NotImplementedError()

    @abstractmethod
    def response(self):
        raise NotImplementedError()
