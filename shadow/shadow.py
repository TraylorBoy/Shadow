"""This module provides an entry point to the Shadow package. Make ShadowBots with the ShadowBuilder and deploy them to the ShadowNetwork"""

from shadow.builder import ShadowBuilder


class Shadow:

    """Facade class that provides the ShadowBuilder and ShadowNetwork objects"""

    def __init__(self) -> None:
        """Instantiate the ShadowBuilder and the ShadowNetwork"""

        self.builder = ShadowBuilder()  # Makes ShadowBots

    def build(self, name: str) -> object:
        """Makes an instanstiated ShadowBot object"""

        return self.builder.make(name, "default")
