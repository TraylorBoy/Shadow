"""Proxy to the given ShadowBot in order to communicate with it while running on its seoerate process
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from loguru import logger

from shadow.bot import ShadowBot


class IShadowProxy(ABC):

    """Proxy Interface"""

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    



class ShadowProxy(IShadowProxy):

    """Proxy Implementation"""

    def __init__(self):
        """Creates a proxy for the given ShadowBot"""
        pass
