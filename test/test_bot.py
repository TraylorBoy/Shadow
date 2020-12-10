from time import sleep
from typing import Dict, Optional

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


def sleep_task(sleep_for: int):

    sleep(sleep_for)

    return True


def true_task():
    return True


def pass_task():
    pass


def test_rename():

    assert shadowbot.name is None

    change_name(to="Rename Test")

    assert shadowbot.name == "Rename Test"


def test_state():

    assert turn_on()
    assert turn_off()


def test_task():

    kwargs: Dict[str, int] = {"sleep_for": 1}

    shadowbot.add_task(signal="sleep", task=sleep_task, task_args=kwargs)

    turn_on()

    assert shadowbot.run(signal="sleep", wait=True)

    turn_off()

    assert shadowbot.run(signal="sleep", wait=True) is None

    turn_on()

    shadowbot.add_task(signal="truth", task=true_task)

    shadowbot.run(signal="truth")

    sleep(1)

    assert shadowbot.get_result(signal="truth")

    shadowbot.remove_task(signal="sleep")

    shadowbot.remove_task(signal="truth")

    assert not shadowbot.check_task(signal="sleep")

    assert not shadowbot.check_task(signal="truth")

    shadowbot.add_task(signal="pass", task=pass_task)

    shadowbot.run(signal="pass")

    assert not shadowbot.get_result(signal="pass")
