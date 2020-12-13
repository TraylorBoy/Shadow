import time

import pytest

from shadow.clone import ShadowClone


@pytest.fixture
def clone():
    return ShadowClone()


def always_true():
    return True


def sleep(sleep_for: int = 1):
    time.sleep(sleep_for)
    return True


def assign_always_true(clone):

    clone.assign(func=always_true)


def assign_sleep(clone):

    func_args = {"sleep_for": 3}

    clone.assign(func=sleep, **func_args)


def test_clone(clone):
    assert clone.task is None
    assert clone.history.empty()
    assert clone.clone() is not clone


def test_assign(clone):
    prev_task = clone.task

    assign_sleep(clone)
    assert clone.task is not prev_task

    new_task = clone.task

    assign_always_true(clone)
    assert clone.task is not new_task


def test_perform(clone):
    assign_always_true(clone)
    assert clone.perform() is None
    assert clone.unfinished() == 1
    assert clone.check() is None
    assert clone.check(wait=True)

    assert clone.perform(block=True)
    assert clone.unfinished() == 0
    assert not clone.wait()
