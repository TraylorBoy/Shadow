from shadow import Shadow
from shadow.bot import ShadowBot
from shadow.helpers.observer import ShadowObserver

shadow = Shadow()


def test_builder():

    builder = shadow.builder
    factory = builder.factory

    assert factory["default"] is ShadowBot

    shadowbot = builder.make(name="TestBot")

    assert isinstance(shadowbot, ShadowBot)

    assert factory["observer"] is ShadowObserver

    observer = builder.make(name="TestBotObserver", type="observer")

    assert isinstance(observer, ShadowObserver)


def test_build():

    shadowbot = shadow.build(name="TestBot")

    assert shadowbot.name == "testbot"

    shadowbot.build_id = "TestBot2"

    assert shadowbot.name == "testbot2"

    assert cycle_state(shadowbot)

    observer = shadow.observe(shadowbot)

    assert isinstance(observer, ShadowObserver)
    assert observer in shadowbot.state.observers

    unregistered_observers = shadow.unobserve(shadowbot)

    assert observer not in shadowbot.state.observers
    assert observer in unregistered_observers

    assert manual_register(shadowbot)


def cycle_state(shadowbot):

    assert shadowbot.state.is_dead

    shadowbot.state.revive()

    assert shadowbot.state.is_alive

    shadowbot.state.kill()

    assert shadowbot.state.is_dead

    return True


def manual_register(shadowbot):

    builder = shadow.builder

    observer = builder.make(name="TestBotObserver", type="observer")

    shadowbot.state.attach_observer(observer)

    assert observer in shadowbot.state.observers

    shadowbot.state.notify(msg="Hello Test")

    shadowbot.state.notify(log_type="warn", msg="Warn Test")

    shadowbot.state.detach_observer(observer)

    return True
