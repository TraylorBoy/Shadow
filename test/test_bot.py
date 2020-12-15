import pytest

from shadow.bot import ShadowBot


@pytest.fixture
def bot():
    def always_true(): return True

    bot = ShadowBot()
    bot.setup(name="TestBot", tasks={"test": (always_true,)})

    return bot

def test_setup(bot):
    assert bot.name is "TestBot"
    assert bot.messages.empty()
    assert bot.results.empty()


    assert bot.check_task(signal="test")
    assert bot.perform_task(signal="test", wait=True)

    bot.perform_task(signal="test")

    assert bot.get_result(signal="test")

def test_run(bot):
    assert not bot.alive()
    bot.start()
    assert bot.alive()


