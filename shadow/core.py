"""Entry point to the Shadow project"""

from typing import Optional

from shadow.bot import ShadowBot


class Shadow:

    """Interface for making ShadowBots and building the ShadowNetwork"""

    def __init__(self):
        """Instantiates sub-components"""

        # TODO
        self.network = None
        self.builder = None

    def make(self, name: Optional[str] = None) -> ShadowBot:
        """Constructs ShadowBots with provided args"""

        # Create ShadowBot
        shadowbot: ShadowBot = ShadowBot()

        # Build part
        shadowbot.rename(new_name=name)

        # Return product
        return shadowbot
