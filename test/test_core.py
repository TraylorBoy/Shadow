
import pytest
import shadow
import asyncio
from threading import Thread
from multiprocessing import Process, Queue

# ---------------------------------------------------------------------------- #
#                                   Fixtures                                   #
# ---------------------------------------------------------------------------- #

@pytest.fixture
def tasks():
    return shadow.helpers.Tasks

# ---------------------------------------------------------------------------- #
#                                     Tests                                    #
# ---------------------------------------------------------------------------- #

# ------------------------ ShadowProxy & ShadowNetwork ----------------------- #

async def proxy():

    proxy = shadow.ShadowProxy()

    p = Process(target=proxy.serve)

    p.start()

    await asyncio.sleep(1)

    res = await proxy.network.send(message={"event": "status", "data": None})

    assert res["data"] == "Alive"

    await proxy.network.kill()

    p.join()

    return True


@pytest.mark.asyncio
async def test_proxy():
    assert await proxy()


# -------------------------------- ShadowClone ------------------------------- #

def clone(tasks):
    results = Queue()

    shadowclone = shadow.ShadowClone(id="flip", pipe=results, task=tasks["test"]["flip"])

    assert shadowclone.name == "flip"
    assert shadowclone.pipe is results
    assert not shadowclone.alive()
    assert not shadowclone.wait()

    Thread(target=shadowclone.perform).start()

    assert shadowclone.wait()

    assert not results.empty()
    task, result = results.get(block=True)

    assert task == "flip"
    assert not result

    return True

def test_clone(tasks):
    assert clone(tasks)

# --------------------------------- ShadowBot -------------------------------- #

def bot(tasks):

    shadowbot = shadow.ShadowBot(name="TestBot", tasks=tasks["test"])
    manager = shadow.Needles()

    manager.sew(bot=shadowbot)
    assert manager.check(bot=shadowbot)

    assert shadowbot.id == "TestBot"
    assert "flip" in shadowbot.clones.keys()
    assert not shadowbot.get()
    assert not shadowbot.listen()

    shadowbot.start()
    assert shadowbot.alive()

    shadowbot.pipe["task"].put("flip", block=True)
    shadowbot.pipe["event"].put("task", block=True)
    shadowbot.pipe["wait"].put("flip", block=True)
    shadowbot.pipe["event"].put("wait", block=True)
    shadowbot.pipe["event"].put("compile", block=True)

    if not shadowbot.pipe["response"].empty():

        task, result = shadowbot.pipe["response"].get()

        assert task == "flip"
        assert not result

    shadowbot.kill()
    assert not shadowbot.alive()

    return True

def test_bot(tasks):
    assert bot(tasks)




