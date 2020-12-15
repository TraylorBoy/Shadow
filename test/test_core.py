import pytest

from shadow.core import Shadow


@pytest.fixture
def core():
    return {"shadow": Shadow(), "proxy": Shadow().build()}

@pytest.fixture
def proxy(core):
    return core["shadow"].build(name="TestBot")

def test_build(core, proxy):
    assert core["proxy"].bot.name is None
    assert proxy.bot.name == "TestBot"
    core["shadow"].edit(proxy=proxy, name="Tea")
    assert proxy.bot.name == "Tea"

