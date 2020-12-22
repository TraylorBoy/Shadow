"""Command line application for the Shadow project"""

import os
import time
from typing import Callable, Dict, List

from shadow.bot import ShadowBot
from shadow.cache import ShadowCache
from shadow.helpers.signals import TEST_SIGNALS
from shadow.proxy import ShadowProxy
from shadow.task import ShadowTask


class Shadow(object):

    """Application entry point"""

    def __init__(self):
        """Setup the interactive command line script"""

        # Setup session
        self.__setup()

        # Invoker
        self.COMMANDS: Dict[str, Callable] = {
            "new": self.__setup,
            "load": self.__load,
            "start": self.__run,
            "stop": self.__kill,
            "observe": self.__watch,
            "unobserve": self.__unwatch,
        }

        # Console message
        self.menu: str = f"""
                COMMANDS: {list(self.COMMANDS.keys())}

                ShadowBots
                ----------
                {list(self.possession.keys())}
            """

    def __setup(self):
        """Setup interactive session"""

        print("\nStarting new session")

        # Tracks ShadowBots during session
        self.possession: Dict[str, object] = {}

        # Load souls from data if there are any
        souls: List[str] = os.listdir("shadow/data/souls")

        if len(souls) > 0:
            for soul in souls:
                soul = soul.strip(".soul")

                # Instantiate bot with soul
                self.possession[soul] = ShadowProxy(shadowbot=ShadowBot(name=soul))

        else:

            # No souls stored, create default
            self.__new()

        # Cache keys
        with ShadowCache() as cache:
            cache.store(key="possession", value=list(self.possession.keys()))

    def __load(self):
        """Loads stored bots from cache"""

        print("\nLoading bots from cache")

        with ShadowCache() as cache:

            if cache.retrieve(key="possession") is not None:

                bot_ids: List[str] = cache.retrieve(key="possession")

                for _id in bot_ids:
                    self.possession[_id] = ShadowProxy(shadowbot=ShadowBot(name=_id))

    def __new(self):
        """Creates a new interactive session"""

        with ShadowCache() as cache:

            print("Creating new session")

            # Create default test bot
            default_tasks: object = ShadowTask()
            default_tasks.add(name="true", task=TEST_SIGNALS["true"])
            default_tasks.add(name="sleep", task=TEST_SIGNALS["sleep"], len=3)

            self.possession = {
                "TestBot": ShadowProxy(
                    shadowbot=ShadowBot(name="TestBot", shadow_task=default_tasks)
                )
            }

            # Store keys in cache so that they can be restored
            cache.store(key="possession", value=list(self.possession.keys()))

    def __run(self):
        """Starts the ShadowBot specified by user input"""

        bot_id: str = str(input("ShadowBot Name: "))
        daemonize: str = str(input("Run ShadowBot in the background (y/n)?: ")) or "n"

        is_daemon: bool = True if daemonize == "y" else False

        if bot_id in self.possession.keys():
            self.possession[bot_id].daemonize() if is_daemon else self.possession[
                bot_id
            ].start()

        else:
            print("Invalid ID")

    def __kill(self):
        """Stops the running ShadowBot specified by user input"""

        bot_id: str = str(input("ShadowBot Name: "))

        if bot_id in self.possession.keys():
            self.possession[bot_id].stop()

        else:
            print("Invalid ID")

    def __watch(self):
        """Register observer for ShadowBot specified by user input"""

        bot_id: str = str(input("ShadowBot Name: "))

        if bot_id in self.possession.keys():
            self.possession[bot_id].observe()

        else:
            print("Invalid ID")

    def __unwatch(self):
        """Removes registered observer from ShadowBot specified by user input"""

        bot_id: str = str(input("ShadowBot Name: "))

        if bot_id in self.possession.keys():
            self.possession[bot_id].unobserve()

        else:
            print("Invalid ID")

    def start(self):
        """Starts the interactive command line script"""

        while True:

            print(self.menu)

            command: str = str(input("Enter command (Press enter to quit): ")) or "exit"

            command = command.lower()

            if command == "exit":
                # Stop all Bots
                for _, proxy in self.possession.items():
                    proxy.kill() if proxy.is_daemon() else proxy.stop()
                break

            elif command in self.COMMANDS.keys():

                self.COMMANDS[command]()
                time.sleep(1)

            else:
                print(f"\nInvalid Command: {command}\n")
