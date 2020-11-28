"""This module provides an entry point to the Shadow package. Make ShadowBots with the ShadowBuilder and deploy them to the ShadowNetwork"""

import logging

from shadow.builder import ShadowBuilder

logging.basicConfig(level=logging.INFO)


class Shadow:

    """Facade class that provides the ShadowBuilder and ShadowNetwork objects"""

    def __init__(self) -> None:
        """Instantiate the ShadowBuilder and the ShadowNetwork"""

        self.builder = ShadowBuilder()  # Makes ShadowBots

    def build(self, name: str) -> object:
        """Makes an instanstiated ShadowBot object"""

        return self.builder.make(name, "default")

    def observe(self, shadowbot: object) -> object:
        """Instantiates and registers a ShadowObserver to the supplied ShadowBot"""

        observer = self.builder.make(name="TestBotObserver", type="observer")

        shadowbot.state.attach_observer(observer)  # type: ignore

        return observer

    def unobserve(self, shadowbot: object) -> list:
        """Deregister all observers registered to the supplied ShadowBot"""

        unregistered = []

        for observer in shadowbot.state.observers:  # type: ignore
            shadowbot.state.detach_observer(observer)  # type: ignore
            unregistered.append(observer)

        return unregistered
