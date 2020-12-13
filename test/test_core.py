import pytest

from shadow.core import Shadow


@pytest.fixture
def core():
    return {"shadow": Shadow(), "bot": Shadow().build()}


@pytest.fixture
def observer(core):
    return core["shadow"].observe(bot=core["bot"])


def test_build(core):
    assert core["bot"].name is None
    assert core["shadow"].build(name="TestBot").name == "TestBot"


def test_observe(core, observer):
    assert observer in core["bot"].observers


def test_unobserve(core, observer):
    core["shadow"].unobserve(bot=core["bot"], observer=observer)
    assert observer not in core["bot"].observers
