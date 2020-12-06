"""State machine that manages ShadowBot state and updates observers of state changes"""

from statemachine import State, StateMachine


class ShadowState(StateMachine):

    """Provides states and their transitions for the ShadowBot class"""

    alive = State("Alive")
    dead = State("Dead", initial=True)

    revive = dead.to(alive)
    kill = alive.to(dead)
