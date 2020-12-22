"""Command line application for the Shadow project"""

import os
from typing import Dict, List

import click

from shadow.bot import ShadowBot
from shadow.cache import ShadowCache
from shadow.helpers.signals import TEST_SIGNALS
from shadow.proxy import ShadowProxy
from shadow.task import ShadowTask


class Core(object):

    """Application entry point"""

    def __init__(self):
        """Setup the interactive command line script"""

        # Setup session
        self.__setup()

    def __setup(self):
        """Setup interactive session"""

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
            self.new()

        # Cache keys
        with ShadowCache() as cache:
            cache.store(key="possession", value=list(self.possession.keys()))

    def new(self):
        """Creates a default ShadowBot and stores it"""

        with ShadowCache() as cache:

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


core: Core = Core()


@click.group()
def Shadow():
    pass


@Shadow.command()
def list():
    for _id in core.possession:
        click.echo(_id)
