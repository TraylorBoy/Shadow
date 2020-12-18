import pytest

from shadow.proxy import ShadowProxy


@pytest.fixture
def proxy():
    def always_true():
        return True

    proxy = ShadowProxy()
    proxy.bot.add_task(signal="test", task=(always_true,))
    return proxy


def test_connection(proxy):
    assert proxy.bot.name is None
    assert proxy.observer is None
    assert "test" in proxy.bot.clones.keys()

    proxy.observe()
    assert proxy.observer in proxy.bot.observers

    proxy.unobserve()
    assert proxy.observer not in proxy.bot.observers

    proxy.start()
    assert proxy.alive()

    assert proxy.send(signal="test", wait=True)

    proxy.send(signal="test", wait=False)
    assert proxy.wait(signal="test")

    proxy.stop()
    assert not proxy.alive()
