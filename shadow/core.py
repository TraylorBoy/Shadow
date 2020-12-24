"""Command line application for the Shadow project"""

import os
from typing import Dict, List

import click

from shadow.bot import ShadowBot
from shadow.cache import ShadowCache
from shadow.signals import ShadowSignal
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

                # Bot used for test purposes
                if soul == "TestBot":
                    continue

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
            default_tasks.add(name="true", task=ShadowSignal().TEST["true"])
            default_tasks.add(name="sleep", task=ShadowSignal().UTILITIES["sleep"], len=3)

            self.possession = {
                "ShadowBot": ShadowProxy(
                    shadowbot=ShadowBot(name="ShadowBot", shadow_task=default_tasks)
                )
            }

            # Store keys in cache so that they can be restored
            cache.store(key="possession", value=list(self.possession.keys()))


core: Core = Core()


@click.group()
def Shadow():
    pass

@Shadow.command()
def bots():
    """Lists all ShadowBots and their state
    """

    for _id in core.possession:
        click.echo(f"\n{_id} - {'Alive' if core.possession[_id].alive() else 'Dead'}")

    click.echo("\n")

@Shadow.command()
def signals():
    """Lists all signals that are attached to the given ShadowBot

    If none is given, lists all signals for every ShadowBot
    """

    for _id in core.possession:
        click.echo(f"\n{_id} - {core.possession[_id].list_signals()}")

    click.echo("\n")

@Shadow.command()
@click.argument("name", required=1)
def run(name):
    """Start running the ShadowBot process
    """

    if name in core.possession.keys():

        core.possession[name].observe()
        core.possession[name].start()

    else:

        click.echo(f"\n{name} does not exist\n")


@Shadow.command()
@click.argument("name", required=1)
def stop(name):
    """Stop running the ShadowBot process
    """

    if name in core.possession.keys() and core.possession[name].alive():

        core.possession[name].stop()

    else:

        click.echo(f"\n{name} does not exist\n")

@Shadow.command()
@click.argument("name", required=1)
@click.argument("signal", required=1)
def perform(name, signal):
    """Have a ShadowBot perform a task
    """

    if name in core.possession.keys() and core.possession[name].alive():

        core.possession[name].perform(signal=signal)

    else:

        click.echo(f"\n{name} does not exist\n")

@Shadow.command()
def compile():
    """Get the result from a completed task
    """
    pass

@Shadow.command()
def daemonize():
    """Have a ShadowBot run in the background
    """
    pass

