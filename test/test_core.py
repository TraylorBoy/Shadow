
import time
import shadow
import pytest

from multiprocessing import Process
from shell import shell

from typing import Any, Optional, Dict

# ---------------------------------------------------------------------------- #
#                                    Helpers                                   #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
#                                   Fixtures                                   #
# ---------------------------------------------------------------------------- #

@pytest.fixture
def proxy():
    return shadow.proxy.ShadowProxy()

@pytest.fixture
def tasks():
    return shadow.helpers.Tasks

@pytest.fixture
def server():

    p: Process = Process(target=shell, args=("shadow serve",), daemon=True)
    p.start()

    time.sleep(1)
    return p

# ---------------------------------------------------------------------------- #
#                                     Tests                                    #
# ---------------------------------------------------------------------------- #

def test_bot_proxy(proxy, tasks):

    pass

def test_proxy(proxy, tasks, server):

    assert server.is_alive()

    response: Optional[Dict[str, Optional[Any]]] = proxy.send(message={
        "event": "status",
        "data": None
    })

    assert response["data"]["server"] == "Alive"

    response = proxy.sew(name="Test", tasks=tasks["test"])

    assert "Test" in response["data"]

    response = proxy.signal(name="Test", event="status", task="")

    assert not response["data"]["alive"]

    response = proxy.retract(name="Test")

    assert "Test" in response["data"]["needle"].keys()

    response = proxy.kill()

    server.join()

    assert response["data"] == "Shutting down"
