"""State machine that manages ShadowBot state and updates observers of state changes"""

from typing import Callable

from statemachine import State, StateMachine

from shadow.helpers.observer import Observable


class ShadowState(StateMachine, Observable):

    """Provides states and their transitions for the ShadowBot class"""

    alive: State = State("Alive")
    dead: State = State("Dead", initial=True)

    revive: Callable = dead.to(alive)
    kill: Callable = alive.to(dead)
