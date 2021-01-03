import pytest
import time

from multiprocessing import Queue
from threading import Thread

from shadow import ShadowBot, ShadowBotProxy, ShadowClone, ShadowNetwork, Needles
from shadow.helpers import Tasks

from functools import partial
from typing import Tuple, Dict

@pytest.fixture
def result_que():
    return Queue()

def test_clone(result_que):

    clone: ShadowClone = ShadowClone(pipe=result_que, task=Tasks["test"]["flip"])

    t: Thread = Thread(target=clone.perform, name="flip")
    t.start()
    t.join()

    if not result_que.empty():
        task, result = result_que.get()

        assert task == "flip" and result == False

def test_bot():

    bot: ShadowBot = ShadowBot(name="TestBot", tasks=Tasks["test"])

    assert bot.id == "TestBot"
    assert bot.manager is Tasks["test"]

    bot.start()
    assert bot.alive()
    assert bot.start() is None

    bot.stop()
    assert not bot.alive()
    assert bot.stop() is None

    bot.start()
    assert bot.alive()

    bot.request(type="perform", task="flip")
    bot.request(type="wait", task="flip")

    task, result = bot.response()

    assert task == "flip" and result == False

    bot.stop()
    assert not bot.alive()

def test_bot_proxy():

    proxy: ShadowBotProxy = ShadowBotProxy(name="TestBot", tasks=Tasks["test"])

    proxy.start()
    assert proxy.alive()

    proxy.perform(task="flip")

    task, result = proxy.wait(task="flip")

    assert task == "flip" and result == False

    proxy.stop()
    assert not proxy.alive()

def test_needles():

    needles: Needles = Needles()
    needles.reset()

    assert not needles.can_load()

    needles.sew(bot=ShadowBot(name="TestBot", tasks=Tasks["test"]))

    time.sleep(1)

    assert needles.can_load()

    essence: Tuple[str, Dict[str, partial]] = needles.retract(name="TestBot")

    name, tasks = essence
    assert name == "TestBot" and tasks is Tasks["test"]

def test_network():
    network: ShadowNetwork = ShadowNetwork(host="localhost", port=8080)
    network.run_server()

    assert network.bot.alive()

    event, data = network.build(name="TestBot2", tasks=Tasks["test"])

    name, tasks = data

    assert event == "BUILD" and name == "TestBot2" and not tasks["flip"]()

    event, data = network.send(message=("shutdown", None))

    assert event == "SHUTDOWN" and data == True

    assert not network.bot.alive()




