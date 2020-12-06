from time import sleep
from typing import Callable, List

from shadow.clone import ShadowClone


def create_clone():

    shadowclone: ShadowClone = ShadowClone()

    return shadowclone


def shadow_clone_jutsu(summon_amount: int):

    clones: List = []

    shadowclone: ShadowClone = create_clone()

    for _ in range(summon_amount):
        clones.append(shadowclone.clone())

    return clones


def assign_task(task: Callable, **kwargs):

    shadowclone = ShadowClone()

    shadowclone.assign(func=task, **kwargs)

    return shadowclone


def test_init():

    assert create_clone().task is None


def test_prototype():

    shadow_clones = shadow_clone_jutsu(summon_amount=2)

    assert len(shadow_clones) == 2
    assert shadow_clones[0] is not shadow_clones[1]


def test_task():
    def did_sleep(len: int):
        sleep(len)
        return True

    shadowclone: ShadowClone = assign_task(task=did_sleep, len=1)

    assert shadowclone.task[0] is did_sleep
    assert shadowclone.task[0](**shadowclone.task[1])
    assert shadowclone.perform()
