import pytest

from shadow.bot import ShadowBot


@pytest.fixture
def bot():
    return ShadowBot()


def test_setup(bot):
    assert bot.name is None
    assert not bot.on
    assert bot.messages.empty()
    assert bot.results.empty()
