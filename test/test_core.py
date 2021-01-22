import pytest

from multiprocessing import Queue
from typing import Any, Optional

from shadow import ShadowClone, ShadowBot, ShadowBotProxy, Needle, Needles, ShadowNetwork
from shadow.core.helpers import Tasks

# ----------------------------------- Tasks ---------------------------------- #

def test_tasks():
    """Tests Tasks helper class
    """

    assert Tasks.get(task="does not exist") is None

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
        [Optional[Any]]: Response from ShadowBot instance
    """

    turn_on(bot)

    bot.request(event, task)
    bot.request("wait", task)
    resp: Optional[Any] = bot.response(task)

    turn_off(bot) if event != "kill" else None

    return resp

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

    assert bot.perform(task="does not exist") is None
    assert bot.wait(task="does not exist") is None
    assert bot.jutsu(task="does not exist") is None
    assert bot.alive(task="does not exist") is None
    assert bot.alive(task="sleep") is None
    assert bot.stop() is None
    assert bot.response(task="sleep") is None
    assert isinstance(bot.essence, Needle)

    assert turn_on(bot)
    assert turn_off(bot)
    assert restart(bot)
    assert turn_off(bot)

    assert run(bot, event="stop", task=None) is None
    assert not bot.alive()

    assert run(bot, event="perform", task="sleep")
    assert run(bot, event="perform", task="sum") == 2

def test_bot_proxy(bot):

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

def test_needles(bot):

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


# ---------------------------------- Network --------------------------------- #

def test_network(bot):

    network: ShadowNetwork = ShadowNetwork(host="127.0.0.1", port=8081)

    assert network.kill() is None
    assert network.request(event="none", data=None) is None
    assert network.stop() is None

    assert network.serve()
    assert network.alive()

    event, data = network.request(event="needles")
    assert event == "NEEDLES" and len(data) == 0

    event, successful = network.request(event="build", data=bot.essence)
    assert event == "BUILD" and successful

    event, data = network.request(event="needles")
    assert event == "NEEDLES" and len(data) == 1 and bot.name in data.keys()

    network.kill()
    assert not network.alive()
