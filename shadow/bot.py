"""This module provides a remote task runner i.e. ShadowBot"""

from shadow.helpers.state import ShadowState


class ShadowBot:

    """Bae ShadowBot class"""

    def __init__(self) -> None:
        """Set default properties"""

        self.__id = "Default"  # Used to identify the ShadowBot
        self.state = ShadowState()

    @property
    def name(self) -> str:
        """ShadowBot ID property"""

        return self.__id

    @name.setter  # type: ignore
    def build_id(self, new_name: str) -> None:
        """Build ShadowBot's ID"""

        self.__id = new_name.lower()
