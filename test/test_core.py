import pytest

from multiprocessing import Queue
from threading import Thread

from shadow import ShadowBot, ShadowBotProxy, ShadowClone, ShadowNetwork
from shadow.helpers import Tasks


from typing import Optional, Any, Tuple

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

def test_network():

    network: ShadowNetwork = ShadowNetwork(host="localhost", port=8080)

    assert network.host == "localhost" and network.port == 8080
    assert network.server is not None

    t: Thread = Thread(target=network.serve)
    t.daemon = True
    t.start()

    message: Tuple[str, Optional[Any]] = ("shutdown", None)

    event, data = network.send(message)

    assert event == "SHUTDOWN" and data == True

    if t.is_alive():
        network.kill()
        t.join()


