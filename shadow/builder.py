"""This module provides a builder class to make ShadowBots"""

from shadow.bot import ShadowBot


class ShadowBuilder:

    """ShadowBot builder class"""

    @property
    def factory(self) -> dict:
        """Build factory"""

        return {"default": ShadowBot}

    def make(self, name: str, type: str = "default") -> ShadowBot:
        """Builds a ShadowBot with the supplied configuration"""

        name, type = name.lower(), type.lower()  # Format

        if type not in self.factory.keys():  # pragma: no cover
            raise TypeError("Invalid build type")

        # Retrieve bot from factory
        bot = self.factory[type]()

        # Construct
        bot.build_id = name

        # Return product
        return bot
