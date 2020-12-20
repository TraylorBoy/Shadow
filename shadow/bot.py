"""Task Manager"""

import os
from multiprocessing import Process, Queue
from threading import Thread
from typing import Any, Dict, Optional

import dill
from loguru import logger

from shadow.cache import ShadowCache
from shadow.clone import ShadowClone
from shadow.helpers.catcher import ShadowCatch
from shadow.observer import Observable
from shadow.task import ShadowTask

# Wrap logger.catch in order for it to be picked up
logger.catch = ShadowCatch(target=logger.catch)  # type: ignore


class ShadowBot(Observable, object):

    """Master class for running tasks performed by ShadowClones (slaves)"""

    def __repr__(self):
        """Returns a string representation of the ShadowBot

        Returns:
            [str]: ShadowBot properties
        """

        tasks: str = ""

        for signal, clone in self.clones.items():
            tasks += f"{signal} - {clone}\n"

        return f"""
            Name: {self.id}

            Tasks
            -----
            {tasks}
        """

    def __init__(self, name: str, shadow_task: ShadowTask):
        """Instantiates ShadowBot with ShadowTask object

        Args:
            name (str): A unique ID used for caching ShadowBot instance
            shadow_task (object): Instantiated ShadowTask instance
        """

        self.id: str = name
        self.clones: Dict[str, Dict[str, Any]] = {}
        self.history: Dict[str, Optional[Any]] = {}

        self.__setup_tasks(manager=shadow_task)
        self.__setup_soul()

        # Store tasks in cache so bot can be revived
        self.zombify()

    def __setup_tasks(self, manager: ShadowTask):
        """Bind task methods and task lists to ShadowBot instance

        Args:
            shadow_task (object): Instantiated ShadowTask instance
        """

        # Keep task manager for re-initializing ShadowBot
        self.task_manager: ShadowTask = manager

        for signal, _partial in self.task_manager.tasks.items():
            # Create new clone for each task
            self.clones[signal] = {
                "slave": ShadowClone(master=self, name=signal, task=_partial),
                "soul": None,
            }

    def __setup_soul(self):
        """ShadowBot runs on a seperate process in order to perform tasks"""

        # Slaves put task results into results Queue
        self.results: Optional[Queue] = Queue()

        # Bot listens for messages put into requests Queue
        self.requests: Optional[Queue] = Queue()

        # Bot sends results to responses Queue
        self.responses: Optional[Queue] = Queue()

        # Process bot runs on
        self.soul: Optional[Process] = Process(target=self.__receive)

    @logger.catch
    def __enter__(self):
        """Starts the process and waits for signals

        Attempts to retrieve ShadowBot instance from cache by ID

        Returns:
            [ShadowBot]: Running ShadowBot instance
        """

        # Retrieve instance from memory cache and start running process
        self.zombify(load=True)
        self.bug(self.soul)

        # Start the process
        self.start()

        return self

    @logger.catch
    def __exit__(self, *exec_info):
        """Stops the process and caches ShadowBot instance"""

        # Stop running process
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

        self.notify("Starting up", pid=os.getpid())

        while True:
            if not self.requests.empty():

                msg = self.requests.get()

                self.notify(f"Message received: {msg}")

                if msg == "stop":
                    self.notify("Shutting down")
                    break

                elif msg == "wait":
                    self.notify("Waiting for tasks to finish")
                    self.wait_all()

                elif msg == "compile":
                    self.notify("Compiling all tasks")
                    self.compile_all()

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

    @logger.catch
    def wait(self, signal: str):
        # Todo: Docstring

        if signal in self.clones.keys():
            self.clones[signal]["soul"].join() if self.__alive(signal=signal) else None

    @logger.catch
    def wait_all(self):

        for signal in self.clones.keys():
            self.wait(signal=signal)

    @logger.catch
    def compile(self, signal: str, run: bool = False):
        # Todo: Docstring

        if signal in self.clones.keys():

            if run:
                self.perform(signal=signal)

            self.wait(signal=signal)

            if signal not in self.history.keys():
                return None

            return self.history[signal]

    @logger.catch
    def compile_all(self):
        # Todo: Docstring

        for signal in self.clones.keys():
            if signal == "compile":
                continue

            self.compile(signal=signal, run=True)

    @logger.catch
    def compiler(self):
        """Runs compiler on seperate thread"""

        # Slave compiles results sent by slaves on a seperate thread
        self.clones["compile"] = {
            "slave": ShadowClone(master=self, name="compile", task=self.__compile),
            "stop": False,
            "soul": None,
        }

        self.perform(signal="compile")

    @logger.catch
    def start(self):
        """Runs the ShadowBot on a seperate process

        ShadowBot starts listening for messages and compiling results
        """

        if not self.soul.is_alive():

            # Start compiling results
            self.compiler()

            # Start process
            self.soul.start()

    @logger.catch
    def stop(self):
        """Stop running the ShadowBot process"""

        if self.soul.is_alive():
            # Send stop message to process
            self.requests.put("stop")

            # Stop compiler thread
            self.clones["compile"]["stop"] = True

            # Wait for process to finish
            self.soul.join()

    @logger.catch
    def zombify(self, load: bool = False):
        """Stores task manager in cache by ID

        Args:
            shadow_task (object): Task list to store in cache
        """

        # Store bot task manager in cache
        with ShadowCache() as cache:
            if not load:

                self.bug("Storing to cache", bot=self)

                cache.store(key=self.id, value=dill.dumps(self.task_manager))

            else:

                mod_soul = dill.loads(cache.retrieve(key=self.id))

                self.__init__(name=self.id, shadow_task=mod_soul)  # type: ignore

                self.bug("Loaded from cache", bot=self)
