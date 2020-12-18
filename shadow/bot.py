"""Task Manager"""

from datetime import datetime
from multiprocessing import Process, Queue
from threading import Thread
from typing import Any, Dict, Optional

from loguru import logger

from shadow.clone import ShadowClone
from shadow.observer import Observable

# Setup log file
logger.add(
    f"shadow/logs/{datetime.now().month}_{datetime.now().day}_{datetime.now().year}.log",
    rotation="500 MB",
    enqueue=True,
)


class ShadowBot(Observable, object):

    """Master class for running tasks performed by ShadowClones (slaves)"""

    def __repr__(self):
        """Returns a string representation of the ShadowBot"""

        tasks: str = ""

        for signal, clone in self.clones.items():
            tasks += f"{signal} - {clone}\n"

        return f"""
            Name: {self.id}

            Tasks
            -----
            {tasks}
        """

    def __init__(self, name: str, shadow_task: object):
        # Todo: Docstring

        self.id: str = name
        self.clones: Dict[str, Dict[str, Optional[object]]] = {}
        self.history: Dict[str, Optional[Any]] = {}

        for signal, _partial in shadow_task.tasks.items():
            # Create new clone for each task
            self.clones[signal] = {
                "slave": ShadowClone(master=self, name=signal, task=_partial),
                "soul": None,
            }

        # Run task compiler
        self.results: Queue = Queue()

        self.clones["compile"] = {
            "slave": ShadowClone(master=self, name="compile", task=self.__compile),
            "stop": False,
            "soul": None,
        }

        self.perform(signal="compile")

        # Setup process
        self.requests: Queue = Queue()
        self.responses: Queue = Queue()
        self.soul: Process = Process(target=self.__receive)
        self.on: bool = False

    def __enter__(self):
        # Todo: Docstring

        self.start()

        return self

    def __exit__(self, *exec_info):
        # Todo: Docstring

        self.clones["compile"]["stop"] = True
        self.stop()

    def __del__(self):
        # Todo: Docstring

        self.clones["compile"]["stop"] = True
        self.stop()

    def __shadow_clone_jutsu(self, signal: str):
        # Todo: Docstring

        shadow_clone: ShadowClone = self.clones[signal]["slave"]
        self.clones[signal]["soul"] = Thread(target=shadow_clone.perform)

    def __alive(self, signal: str):
        # Todo: Docstring

        if self.clones[signal]["soul"] is not None:
            return self.clones[signal]["soul"].is_alive()
        else:
            return False

    @logger.catch
    def __compile(self):
        # Todo: Docstring

        while True:
            if self.clones["compile"]["stop"]:
                break

            if not self.results.empty():
                slave, result = self.results.get()

                if self.soul.is_alive():
                    self.responses.put((slave, result))
                    self.bug("Compiled result added to responses")

                self.history[slave] = result

                self.bug(f"Updated history for slave: {slave}")

        return 0

    @logger.catch
    def __receive(self):
        # Todo: Docstring

        self.notify("Starting up")

        while True:
            if not self.requests.empty():

                msg = self.requests.get()

                self.notify(f"Message received: {msg}")

                if msg == "stop":
                    self.notify("Shutting down")
                    break

                else:
                    self.notify(f"Performing task: {msg}")
                    self.perform(signal=msg)

        return 0

    @logger.catch
    def perform(self, signal: str):
        # Todo: Docstring

        # Create thread
        self.__shadow_clone_jutsu(signal=signal)

        if signal in self.clones.keys():
            self.clones[signal]["soul"].start()

    def wait(self, signal: str):
        # Todo: Docstring

        if signal in self.clones.keys():
            self.clones[signal]["soul"].join() if self.__alive(signal=signal) else None

    def compile(self, signal: str, run: bool = False):
        # Todo: Docstring

        if signal in self.clones.keys():

            if run:
                self.perform(signal=signal)

            self.wait(signal=signal)

            if signal not in self.history.keys():
                return None

            return self.history[signal]

    def compile_all(self):
        # Todo: Docstring

        for signal in self.clones.keys():
            if signal == "compile":
                continue

            self.compile(signal=signal, run=True)

    def start(self):
        # Todo: Docstring

        if not self.soul.is_alive():
            self.soul.start()

    def stop(self):
        # Todo: Docstring

        if self.soul.is_alive():
            self.requests.put("stop")
            self.soul.join()
