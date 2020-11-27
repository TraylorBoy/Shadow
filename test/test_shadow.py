from shadow import Shadow
from shadow.bot import ShadowBot

shadow = Shadow()


def test_builder():

    assert shadow.builder is not None
    assert shadow.builder.factory is not None
    assert shadow.builder.factory["default"] is ShadowBot


def test_build():

    shadowbot = shadow.build(name="TestBot")

    assert shadowbot is not None
    assert shadowbot.name == "testbot"

    shadowbot.build_id = "TestBot2"

    assert shadowbot.name == "testbot2"

    assert shadowbot.state is not None
    assert shadowbot.state.is_dead

    shadowbot.state.revive()

    assert shadowbot.state.is_alive

    shadowbot.state.kill()

    assert shadowbot.state.is_dead
