"""This module provides a state machine for the ShadowBot class"""


from statemachine import State, StateMachine

from shadow.helpers.observer import Observable


class ShadowState(StateMachine, Observable):

    """Class for managing the state of a ShadowBot"""

    managing = None  # type: object # ShadowBot assigns self upon instantiating

    dead = State("Dead", initial=True)
    alive = State("Alive")

    revive = dead.to(alive)
    kill = alive.to(dead)

    def on_revive(self) -> None:
        """Transitions from dead to alive, starts running receiver, and notifies observers"""

        self.notify(sender=self.managing.name, msg="State changed from dead to alive")  # type: ignore

    def on_kill(self) -> None:
        """Transitions from alive to deadd, stops receiver, and notifies observers"""

        self.notify(sender=self.managing.name, msg="State changed from alive to dead")  # type: ignore
