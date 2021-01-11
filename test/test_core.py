import pytest

from multiprocessing import Queue
from typing import Any, Optional, Tuple

from shadow import ShadowClone, ShadowBot
from shadow.helpers import Tasks

# -------------------------------- ShadowClone ------------------------------- #

def clone(task: str, *args, **kwargs):
    """Creates a ShadowClone to perform the given task

    Args:
        task (str): Task to perform

    Returns:
        [Any]: Result from task or False if task did not complete
    """

    results: Queue = Queue()
    clone: ShadowClone = ShadowClone(name=task, args=(Tasks.get(task, *args, **kwargs), results))

    clone.start()
    clone.join()

    return results.get()

def test_clone():
    """Tests the ShadowClone Thread subclass
    """

    result: Any = clone(task="sleep", sleep_for=3)
    assert not isinstance(result, bool)

    task, did_sleep = result
    assert task == "sleep" and did_sleep

# --------------------------------- ShadowBot -------------------------------- #

def turn_on(bot: ShadowBot):
    """Turn the ShadowBot on

    Args:
        bot (ShadowBot): ShadowBot instance to start running

    Returns:
        [bool]: ShadowBot successfully started or not
    """

    bot.start()
    return bot.alive()

def turn_off(bot: ShadowBot):
    """Turn the ShadowBot off

    Args:
        bot (ShadowBot): ShadowBot instance to stop running

    Returns:
        [bool]: ShadowBot successfully stopped or not
    """

    bot.stop()
    return not bot.alive()

def restart(bot: ShadowBot):
    """Turn off and turn back on the ShadowBot

    Args:
        bot (ShadowBot): ShadowBot instance to restart

    Returns:
        [bool]: ShadowBot successfully restarted or not
    """

    bot.restart()
    return bot.alive()

def run(bot: ShadowBot, event: str, task: Optional[str]):

    turn_on(bot)

    bot.request(event, task)
    resp: Tuple[str, Any] = bot.response(task)

    turn_off(bot) if event != "stop" else None

    return resp[1]

@pytest.fixture
def bot():
    """ShadowBot instance

    Returns:
        [ShadowBot]: Instantiated with factory tasks
    """

    _tasks = {
        "sleep": Tasks.get("sleep", sleep_for=1),
        "sum": Tasks.get("sum", 1, 1)
    }

    return ShadowBot(name="TestBot", tasks=_tasks)

def test_bot(bot):
    """Tests the ShadowBot class
    """

    assert bot.perform(task="does not exist") is None
    assert bot.wait(task="does not exist") is None
    assert bot.jutsu(task="does not exist") is None
    assert bot.result(task="does not exist") is None
    assert bot.hist(task="does not exist") is None
    assert bot.alive(task="does not exist") is None
    assert bot.alive(task="sleep") is None
    assert bot.stop() is None
    assert bot.response(task="sleep") is None

    assert turn_on(bot)
    assert turn_off(bot)
    assert restart(bot)
    assert turn_off(bot)

    assert run(bot, event="stop", task=None)
    assert run(bot, event="perform", task="sleep")

    _sum: int = run(bot, event="perform", task="sum")
    assert _sum == 2
