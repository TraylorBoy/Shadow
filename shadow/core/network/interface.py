"""Interfaces for the Shadow package"""

from typing import Optional, Any

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
    def alive(self):
        raise NotImplementedError()

    @abstractmethod
    def request(self, event: str, data: Optional[Any]):
        raise NotImplementedError()
