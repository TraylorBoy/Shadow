import pytest
import time
from shadow.bot import ShadowBot


@pytest.fixture
def bot():
    def always_true(): return True

    def sleep_for(len):
        time.sleep(len)
        return True

    sleep_for_args = {
        "len": 1
    }

    bot = ShadowBot()
    bot.name = "TestBot"
    bot.add_task(signal="test", task=(always_true,))
    bot.add_task(signal="sleep", task=(sleep_for, sleep_for_args))

    return bot

def test_init(bot):
    assert bot.name is "TestBot"
    assert bot.messages.empty()
    assert bot.results.empty()
    assert not bot.soul.is_alive()

    assert bot.check_task(signal="test")
    assert bot.perform_task(signal="test", wait=True)

    assert bot.check_task(signal="sleep")
    bot.perform_task(signal="sleep")
    assert bot.get_result(signal="sleep")

def test_run(bot):
    assert not bot.soul.is_alive()

    bot.soul.start()
    assert bot.soul.is_alive()

    bot.messages.put(("sleep", True))
    bot.messages.put(("result", "sleep"))
    result = bot.results.get()
    assert result

    bot.messages.put(("test", False))
    time.sleep(1)
    bot.messages.put(("result", "test"))
    result = bot.results.get()
    assert result

    bot.messages.put(("stop"))
    bot.soul.join()
    assert not bot.soul.is_alive()


