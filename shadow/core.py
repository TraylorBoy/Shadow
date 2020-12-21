"""Command line application for the Shadow project"""
# pragma: no cover

from typing import Dict, List

from shadow.bot import ShadowBot
from shadow.cache import ShadowCache
from shadow.helpers.signals import TEST_SIGNALS
from shadow.task import ShadowTask


class Shadow(object):

    """Application entry point"""

    def __init__(self):
        """Setup the interactive command line script"""

        self.possession: Dict[str, object] = {}

    def __load(self):
        """Loads stored bots from cache"""

        with ShadowCache() as cache:
            if cache.retrieve(key="possession") is not None:
                print("Restoring session")

                bot_ids: List[str] = cache.retrieve(key="possession")

                for _id in bot_ids:
                    self.possession[_id] = ShadowBot(name=_id)

    def __new(self):
        """Creates a new interactive session"""

        with ShadowCache() as cache:

            print("Creating new session")

            # Create default test bot
            default_tasks: object = ShadowTask()
            default_tasks.add(name="true", task=TEST_SIGNALS["true"])
            default_tasks.add(name="sleep", task=TEST_SIGNALS["sleep"], len=3)

            self.possession = {
                "TestBot": ShadowBot(name="TestBot", shadow_task=default_tasks)
            }

            # Store keys in cache so that they can be restored
            cache.store(key="possession", value=list(self.possession.keys()))

    def start(self):
        """Starts the interactive command line script"""

        while True:

            menu: str = f"""
                ShadowBots
                ----------
                {self.possession}
            """

            print(menu)

            command: str = str(input("Enter command: "))

            if command in ["quit", "Quit", "QUIT", "q", "Q", "exit", "Exit", "EXIT"]:
                break

            elif command == "new":
                self.__new()
                continue

            elif command == "load":
                self.__load()
                continue
