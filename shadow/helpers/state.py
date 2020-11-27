"""This module provides a state machine for the ShadowBot class"""

from statemachine import State, StateMachine


class ShadowState(StateMachine):

    """Class for managing the state of a ShadowBot"""

    dead = State("Dead", initial=True)
    alive = State("Alive")

    revive = dead.to(alive)
    kill = alive.to(dead)

    def on_revive(self) -> None:
        """Transitions from dead to alive, starts running receiver, and notifies observers"""
        pass

    def on_kill(self) -> None:
        """Transitions from alive to deadd, stops receiver, and notifies observers"""
        pass
