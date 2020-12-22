"""Task Manager"""

import os
from multiprocessing import Process, Queue
from pathlib import Path
from threading import Thread
from typing import Any, Dict, Optional

import dill
from daemons.prefab import run
from loguru import logger

from shadow.cache import ShadowCache
from shadow.clone import ShadowClone
from shadow.helpers.catcher import ShadowCatch
from shadow.observer import Observable
from shadow.proxy import IShadowProxy
from shadow.task import ShadowTask

# Wrap logger.catch in order for it to be picked up
logger.catch = ShadowCatch(target=logger.catch)  # type: ignore


class ShadowDaemon(run.RunDaemon, object):  # pragma: no cover

    """Daemon wrapper for running ShadowBot in the background"""

    def init(self, master: IShadowProxy):
        """Daemonizes ShadowBot

        Args:
            master (IShadowProxy): ShadowBot to daemonize
        """

        self.master: IShadowProxy = master

    @logger.catch
    def run(self):
        """Runs ShadowBot as a daemon"""

        # Start listening for messages from ShadowBot
        self.master.receiver()
        self.master.compiler()


class ShadowBot(Observable, IShadowProxy, object):

    """Master class for running tasks performed by ShadowClones (slaves)"""

    ID: str = ""

    def __repr__(self):
        """Returns a string representation of the ShadowBot

        Returns:
            [str]: ShadowBot properties
        """

        tasks: str = ""

        for signal in self.clones:
            tasks += f"{signal}() "

        return f"Name: {self.id} Tasks: {tasks}"

    def __init__(self, name: str, shadow_task: Optional[ShadowTask] = None):
        """Instantiates ShadowBot with ShadowTask object

        Args:
            name (str): A unique ID used for caching ShadowBot instance
            shadow_task (object): Instantiated ShadowTask instance
        """

        # Add ShadowBot pidfile for running as a daemon
        self.pidfile = f"shadow/data/daemons/{name}.pid"

        self.__setup_daemon()

        self.id: str = name
        self.ID = name  # Used for PID generation
        self.clones: Dict[str, Dict[str, Any]] = {}
        self.history: Dict[str, Optional[Any]] = {}
        self.keep_alive: bool = (
            False  # Keep the ShadowBot process alive after exiting context manager
        )

        if shadow_task is not None:
            self.__setup_tasks(manager=shadow_task)
            self.__setup_soul()

            # Store tasks in cache so bot can be revived
            self.zombify()
        else:
            # Load from cache
            self.zombify(load=True)

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

    def __setup_daemon(self):
        """Setup daemon wrapper to run instance in the background"""

        Path(self.pidfile).touch()  # Create pidfile in data directory
        self._daemon: ShadowDaemon = ShadowDaemon(
            pidfile=os.path.join(os.getcwd(), self.pidfile)
        )
        self._daemon.init(master=self)

    @logger.catch
    def __enter__(self):
        """Starts the process and waits for signals

        Attempts to retrieve ShadowBot instance from cache by ID

        Returns:
            [ShadowBot]: Running ShadowBot instance
        """

        # Process is already running
        if self.keep_alive:
            return self

        # Retrieve instance from memory cache and start running process
        self.zombify(load=True)

        # Start the process
        self.start()

        return self

    @logger.catch
    def __exit__(self, *exec_info):
        """Stops the process"""

        if not self.keep_alive:
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
    def __receive(self):  # pragma: no cover
        # Todo: Docstring

        self.notify("Starting up")
        self.notify(pid=os.getpid())

        daemonized: bool = self._daemon.pid is not None

        while True:
            if daemonized:
                if self._daemon.pid is None:
                    break
            else:
                if not self.soul.is_alive():
                    break

            if not self.requests.empty():

                msg = self.requests.get()

                self.notify(f"Message received: {msg}")

                if msg == "stop":
                    self.notify("Shutting down")
                    self.keep_alive = False
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
    def compile(self, signal: str):
        # Todo: Docstring

        if signal in self.clones.keys():

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
                continue  # pragma: no cover

            self.compile(signal=signal)

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
    def receiver(self):
        """Runs the receiver on current process"""

        self.__receive()  # pragma: no cover

    @logger.catch
    def start(self):
        """Runs the ShadowBot on a seperate process

        ShadowBot starts listening for messages and compiling results
        """

        if not self.soul.is_alive():

            # Start process
            self.soul.start()

            # Start compiling results
            self.compiler()

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

        if not load:

            self.bug("Storing soul", bot=self)

            with open(f"shadow/data/souls/{self.id}.soul", "wb") as soul:
                dill.dump(self.task_manager, soul)

        else:

            self.bug("Loading soul", bot=self)

            mod_soul: Optional[Any] = None

            with open(f"shadow/data/souls/{self.id}.soul", "rb") as soul:
                mod_soul = dill.load(soul)

            self.__init__(name=self.id, shadow_task=mod_soul)  # type: ignore

    @logger.catch
    def cache(self, load: bool = False):  # pragma: no cover
        """Caches task manager to memory

        Args:
            load (bool, optional): Load task manager from memory. Defaults to False.
        """

        with ShadowCache() as cache:
            if not load:

                self.bug("Storing to cache", bot=self)

                cache.store(key=self.id, value=dill.dumps(self.task_manager))

            else:
                self.bug("Loading from cache", bot=self)

                mod_soul = dill.loads(cache.retrieve(key=self.id))

                self.__init__(name=self.id, shadow_task=mod_soul)  # type: ignore

    @logger.catch
    def daemonize(self):  # pragma: no cover
        """Starts the daemon process"""

        self._daemon.start()

    @logger.catch
    def kill(self):  # pragma: no cover
        """Stops the daemon process"""

        self._daemon.stop()
