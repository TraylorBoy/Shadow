from typing import Optional

from shadow.bot import ShadowBot
from shadow.core import Shadow
from shadow.helpers.observer import ShadowObserver

shadow: Shadow = Shadow()


def make_shadowbot(name: Optional[str] = None):

    shadowbot: ShadowBot = shadow.make(name=name)

    return shadowbot


def observe_shadowbot(bot: ShadowBot):

    observer: ShadowObserver = shadow.observe(bot=bot)

    return observer


def test_make():

    assert make_shadowbot().name is None
    assert make_shadowbot(name="TestBot").name == "TestBot"


def test_observe():

    shadowbot: ShadowBot = make_shadowbot("TestBot")
    observer: ShadowObserver = observe_shadowbot(bot=shadowbot)

    assert observer in shadowbot.observers

    shadowbot.start()
    shadowbot.stop()

    kwargs = {"msg": "test"}

    shadowbot.notify(**kwargs)

    shadow.unobserve(bot=shadowbot, observer=observer)

    assert observer not in shadowbot.observers
