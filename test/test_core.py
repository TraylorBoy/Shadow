import pytest

from multiprocessing import Queue
from typing import Any, Optional, Tuple

from shadow import ShadowClone, ShadowBot, ShadowBotProxy, Needles
from shadow.core.helpers import Tasks

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
    """Runs the ShadowBot and returns the result of the task

    Args:
        bot (ShadowBot): Instantiated ShadowBot instance
        event (str): Event for ShadowBot to handle
        task (Optional[str]): Task to perform

    Returns:
        [Tuple[str, Any]]: Response from ShadowBot instance
    """

    turn_on(bot)

    bot.request(event, task)
    resp: Tuple[str, Any] = bot.response(task)

    turn_off(bot) if event != "kill" else None

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

    assert run(bot, event="kill", task=None)
    assert run(bot, event="perform", task="sleep")

    _sum: int = run(bot, event="perform", task="sum")
    assert _sum == 2

def test_bot_proxy(bot):
    """Tests the ShadowBotProxy class
    """

    proxy: ShadowBotProxy = ShadowBotProxy(essence=bot.essence)

    assert proxy.kill() is None
    assert proxy.wait(task="none") is None
    assert proxy.perform(task="none") is None
    assert proxy.request(event="hi", task=None) is None

    with proxy:
        assert proxy.alive()
        assert proxy.jutsu(task="sleep")
        assert proxy.jutsu(task="sum") == 2

    assert not proxy.alive()

    proxy_two: ShadowBotProxy = ShadowBotProxy(essence=bot.essence)

    # Tests singleton instance
    assert proxy_two.bot is proxy.bot


# ---------------------------------- Network --------------------------------- #

def test_needles(bot):
    """Tests the needles class
    """

    needles: Needles = Needles()
    needles.reset()

    with needles:
        assert not needles.can_load()

        needles.sew(bot.essence)
        assert needles.check(bot.name)

    with needles:
        assert needles.can_load()
        assert needles.check(bot.name)

        shadowbot: ShadowBot = needles.get(bot.name)
        proxy: ShadowBotProxy = ShadowBotProxy(essence=shadowbot.essence)

        assert proxy.bot.name == bot.name

        with proxy:
            assert proxy.jutsu(task="sum") == 2

        needles.retract(bot.name)
        assert not needles.check(bot.name)

def test_server():
    assert True

def test_network():
    assert True

def test_network_proxy():
    assert True

# ---------------------------------- Client ---------------------------------- #

def test_cli():
    assert True
