import pytest

from shadow.core import Shadow

def test_task():
    return True

@pytest.fixture
def core():
    return Shadow()

@pytest.fixture
def proxy(core):
    return core.build(name="TestBot")

def test_build(core, proxy):
    assert core.build().bot.name is None
    assert proxy.bot.name == "TestBot"

def test_edit(core, proxy):
    core.edit(proxy=proxy, name="Tea")
    assert proxy.bot.name == "Tea"

    core.edit(proxy=proxy, signal="test", task=(test_task,))
    assert "test" in proxy.bot.clones.keys()

    core.edit(proxy=proxy, signal="test", remove=True)
    assert "test" not in proxy.bot.clones.keys()

def test_setup(core, proxy):
    core.setup(proxy=proxy, name="TestBot", tasks={"test": (test_task,)})

    assert proxy.bot.name == "TestBot"
    assert "test" in proxy.bot.clones.keys()


