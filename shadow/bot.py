"""Automated task runner"""

from typing import Optional

from loguru import logger


class ShadowBot:

    """Base bot class"""

    def __init__(self):
        """Sets the default name and instantiates the receiver and responder"""

        self.name: Optional[str] = None

        # TODO - Receiver & Responder ShadowClones
        logger.debug("Starting receiver")

        logger.debug("Starting responder")

    def rename(self, new_name: Optional[str] = None):
        """Name setter"""

        self.name = new_name

        logger.debug(f"New name set: {self.name}")
