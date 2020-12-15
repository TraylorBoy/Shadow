import pytest

from shadow.core import Shadow


@pytest.fixture
def core():
    return {"shadow": Shadow(), "proxy": Shadow().build()}


def test_build(core):
    assert core["proxy"].bot.name is None
    assert core["shadow"].build(name="TestBot").bot.name == "TestBot"

