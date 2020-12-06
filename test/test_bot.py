from typing import Optional

from shadow.bot import ShadowBot

shadowbot: ShadowBot = ShadowBot()


def change_name(to: Optional[str] = None):

    shadowbot.rename(new_name=to)


def turn_on():

    shadowbot.activate()

    return shadowbot.alive()


def turn_off():

    shadowbot.deactivate()

    return shadowbot.dead()


def test_rename():

    assert shadowbot.name is None

    change_name(to="Rename Test")

    assert shadowbot.name == "Rename Test"


def test_state():

    assert turn_on()
    assert turn_off()
