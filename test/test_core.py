from functools import partial
from typing import Optional

import pytest

from shadow import ShadowBot, ShadowCache, ShadowObserver, ShadowTask, signals

# ---------------------------------------------------------------------------- #
#                                    Helpers                                   #
# ---------------------------------------------------------------------------- #


def check_task(shadowtask, signal: str):
    return signal in shadowtask.tasks.keys()


def remove_task(shadowtask, signal: str):

    shadowtask.remove(name=signal)

    return not check_task(shadowtask, signal)


# ---------------------------------------------------------------------------- #
#                                   Fixtures                                   #
# ---------------------------------------------------------------------------- #


@pytest.fixture
def tasks():
    return signals.TEST_SIGNALS


@pytest.fixture
def shadowtask(tasks):

    shadowtask: object = ShadowTask()
    shadowtask.add(name="true", task=tasks["true"])
    shadowtask.add(name="sleep", task=tasks["sleep"])
    shadowtask.add(name="true delete", task=tasks["true"])

    return shadowtask


@pytest.fixture
def bot(shadowtask):

    bot: object = ShadowBot(name="TestBot", shadow_task=shadowtask)
    bot.register(observer=ShadowObserver())

    return bot


# ---------------------------------------------------------------------------- #
#                                     Tests                                    #
# ---------------------------------------------------------------------------- #


# -------------------------------- ShadowTask -------------------------------- #


def test_shadowtask(shadowtask):
    assert check_task(shadowtask, signal="true")
    assert check_task(shadowtask, signal="sleep")
    assert remove_task(shadowtask, signal="true delete")

    shadowtask.save(list_name="test")
    shadowtask: object = ShadowTask()

    assert len(shadowtask.tasks) == 0
    assert not check_task(shadowtask, signal="true")

    shadowtask.load(list_name="test")

    assert check_task(shadowtask, signal="true")


# -------------------------------- ShadowCache ------------------------------- #


def test_shadowcache(shadowtask):

    key: str = "true"
    value: bool = True

    with ShadowCache() as cache:
        cache.store(key=key, value=value)

    value = False

    with ShadowCache() as cache:
        value = cache.retrieve(key=key)

    assert value

    name: str = "true"
    task: Optional[partial] = shadowtask.tasks[name]

    assert task()

    with ShadowCache() as cache:
        cache.store(key=name, value=task)

    task = None

    with ShadowCache() as cache:
        task = cache.retrieve(key=name)

    assert task()


# --------------------------------- ShadowBot -------------------------------- #


def test_shadowbot(bot):
    with bot:
        bot.requests.put("true")
        bot.requests.put("wait")

        task, result = bot.responses.get()
        assert task == "true" and result

        bot.requests.put("compile")
        while not bot.responses.empty():
            task, result = bot.responses.get()
            assert result

        assert bot.compile(signal="true", run=True)
