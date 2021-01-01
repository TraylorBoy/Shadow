import pytest
import time

from shadow.bot import ShadowBot
from shadow.proxy import ShadowBotProxy
from shadow.helpers import Tasks

from typing import Any, Optional, Tuple

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
