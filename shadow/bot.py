"""Automated task runner"""

from typing import Any, Callable, Dict, Optional

from loguru import logger

from shadow.clone import ShadowClone
from shadow.helpers.state import ShadowState


class ShadowBot:

    """Base bot class"""

    def __init__(self):
        """Sets the default name and attaches the state machine"""

        self.name: Optional[str] = None
        self.state: ShadowState = ShadowState()
        self.clones: Dict[str, ShadowClone] = {}

    def rename(self, new_name: Optional[str] = None):
        """Name setter"""

        self.name = new_name

        logger.debug(f"New name set: {self.name}")

    def activate(self):
        """Transitions state from dead to alive"""

        logger.debug("Activating")

        self.state.revive()

        # Notify observers
        self.state.notify("State changed from dead to alive")

    def deactivate(self):
        """Transitions state from alive to dead"""

        logger.debug("Deactivating")

        self.state.kill()

        # Notify observers
        self.state.notify("State changed from dead to alive")

    def alive(self):
        """Checks if current state is alive"""

        is_alive: bool = self.state.is_alive

        return is_alive

    def dead(self):
        """Checks if current state is dead"""

        is_dead: bool = self.state.is_dead

        return is_dead

    def add_task(
        self, signal: str, task: Callable, task_args: Optional[Dict[str, Any]] = {}
    ):
        """Delegates task to a ShadowClone which can be called via signal"""

        if signal not in self.clones.keys():
            # Create a clone and assign the task
            clone: ShadowClone = ShadowClone()

            clone.assign(func=task, **task_args)  # type: ignore

            # Clone performs task when signal is called
            self.clones[signal] = clone

    def remove_task(self, signal: str):
        """Removes clone via the signal it is attached to"""

        if signal in self.clones.keys():
            del self.clones[signal]

    def check_task(self, signal: str):
        """Returns true if there is a task attached to signal"""

        return signal in self.clones.keys()

    def run(self, signal: str, wait: bool = False):
        """Performs the task attached to the signal and returns the result"""

        if self.dead():

            logger.warning("Must be alive in order to perform tasks")

            return None

        shadowclone: ShadowClone = self.clones[signal]

        result: Optional[Any] = None

        if wait:
            # Wait for result
            result = shadowclone.perform(block=True)

        else:
            result = shadowclone.perform()

        logger.debug(f"Result compiled: {result}")

        return result

    def get_result(self, signal: str):
        """Returns last result for task attached to signal"""

        if signal in self.clones.keys():

            # Check clone history for result
            result: Any = self.clones[signal].check_history()

            if result is not None:
                return result

            # No result
            return False
