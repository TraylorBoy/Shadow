"""Automated task runner"""

from typing import Optional


class ShadowBot:

    """Base bot class"""

    def __init__(self):
        """Sets the default name and instantiates the receiver and responder"""

        self.name: Optional[str] = None

        # TODO - Receiver & Responder ShadowClones

    def rename(self, new_name: Optional[str] = None) -> None:
        """Name setter"""

        self.name = new_name
