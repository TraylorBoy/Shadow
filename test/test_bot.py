from time import sleep

from shadow.bot import ShadowBot

shadowbot: ShadowBot = ShadowBot()


def test_name():
    assert shadowbot.name is None

    shadowbot.rename(new_name="Rename Test")

    assert shadowbot.name == "Rename Test"


def test_task():
    def sleep_task(for_time: int = 3):
        sleep(for_time)
        return True

    def say_hi():
        print("Hi")
        return True

    shadowbot.add_task(signal="sleep", task=sleep_task, task_args={"for_time": 2})
    shadowbot.add_task(signal="hi", task=say_hi)
    assert shadowbot.check_task(signal="sleep") and shadowbot.check_task(signal="hi")

    shadowbot.remove_task(signal="sleep")
    assert not shadowbot.check_task(signal="sleep")

    assert shadowbot.perform_task(signal="hi", wait=True)
    assert shadowbot.perform_task(signal="hi") is None
    sleep(3)
    assert shadowbot.history()["hi"]


def test_state():
    shadowbot.start()
    assert shadowbot.running()

    shadowbot.messages.put(("hi", True))
    assert shadowbot.results.get()

    shadowbot.messages.put(("hi", False))
    sleep(3)
    shadowbot.messages.put(("history", True))
    assert shadowbot.results.get()["hi"]

    shadowbot.stop()
    assert not shadowbot.running()
