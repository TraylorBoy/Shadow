"""Automated task runner"""

from typing import Optional

from loguru import logger

from shadow.helpers.state import ShadowState


class ShadowBot:

    """Base bot class"""

    def __init__(self):
        """Sets the default name and attaches the state machine"""

        self.name: Optional[str] = None
        self.state: ShadowState = ShadowState()

    def rename(self, new_name: Optional[str] = None):
        """Name setter"""

        self.name = new_name

        logger.debug(f"New name set: {self.name}")

    def activate(self):
        """Transitions state from dead to alive"""

        logger.debug("Activating")

        self.state.revive()

    def deactivate(self):
        """Transitions state from alive to dead"""

        logger.debug("Deactivating")

        self.state.kill()

    def alive(self):
        """Checks if current state is alive"""

        is_alive: bool = self.state.is_alive

        return is_alive

    def dead(self):
        """Checks if current state is dead"""

        is_dead: bool = self.state.is_dead

        return is_dead
