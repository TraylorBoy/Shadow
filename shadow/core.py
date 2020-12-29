"""Command line application for the Shadow project"""

from asyncio.events import AbstractEventLoop
import os
import click
import dill
import time
import asyncio

from shell import shell

from typing import Optional, Tuple, Any, Dict

from shadow import ShadowProxy, Needles


class Core(object):

    """Application entry point

    Provides a simple facade for the Shadow package
    """

    def __init__(self):
        """Setup the interactive console"""

        self.host, self.port = "127.0.0.1", 8888
        self.load()

    def load(self):
        """Loads settings from cache"""

        if os.path.exists("shadow/data/cache/connection.cache"):
            with open("shadow/data/cache/connection.cache", "rb") as cache_file:
                self.host, self.port = dill.load(cache_file)

        self.proxy: ShadowProxy = ShadowProxy(self.host, self.port)

    def store(self, value: Any):
        """Caches value

        Args:
            value (Any): Value to cache
        """

        with open("shadow/data/cache/connection.cache", "wb") as cache_file:
            dill.dump(value, cache_file)

    # --------------------------------- Commands --------------------------------- #

    def serve(self, host: str, port: int):
        """Starts running the server on the given host and port

        Args:
            host (str): Host to run server on
            port (int): Port to communicate with the server
        """

        self.proxy: ShadowProxy = ShadowProxy(host, port)

        self.store(value=(host, port))

        self.proxy.serve()

    def reset(self):
        """Removes settings from cache"""

        click.echo("Restoring default settings...")

        if os.path.exists("shadow/data/cache/connection.cache"):
            os.remove("shadow/data/cache/connection.cache")

        # Remove stored ShadowBots
        Needles().reset()

        click.echo("Restored")

    def send(self, message: Dict[str, Optional[Any]]):
        """Sends a message to the server

        Args:
            message (str): Message to send to the server
        """

        response: Optional[Dict[str, Optional[Any]]] = self.proxy.send(message)

        return response

    def retract(self, name: str):
        """Removes the sewn ShadowBot from the network

        Args:
            name (str): Name used to identify the ShadowBot
        """

        response: Optional[Dict[str, Optional[Any]]] = self.proxy.retract(name)

        return response

    def kill(self):
        """Stops the running server"""

        response: Optional[Dict[str, Optional[Any]]] = self.proxy.kill()

        return response

    def signal(self, name: str, event: str, task: str):
        """Sends a signal to the running ShadowBot process

        Args:
            name (str): Name used to identify the ShadowBot
            event (str): Event for ShadowBot to handle
            task (str): Task for ShadowBot to perform
        """

        response: Optional[Dict[str, Optional[Any]]] = self.proxy.signal(
            name, event, task
        )

        return response

    def status(self):
        """Sends a status event to the running ShadowBot"""

        message: Dict[str, Optional[Any]] = {"event": "status", "data": None}

        response: Optional[Any] = self.send(message)

        return response


@click.group()
def Shadow():
    """Click group entry point"""

    pass


@Shadow.command()
@click.option("--host", default="127.0.0.1", help="Host to run server on")
@click.option("--port", default=8888, help="Port to server communicates on")
def serve(host, port):
    """Start the ShadowNetwork"""

    core: Core = Core()
    core.serve(host, port)


@Shadow.command()
def status():
    """Sends a status message to the server"""

    Core().status()


@Shadow.command()
def kill():
    """Stops the running server"""

    Core().kill()


@Shadow.command()
def reset():
    """Removes ShadowBots from the server and cache files"""

    Core().reset()


@Shadow.command()
def sew():
    """Executes the build script in current directory

    The build script connects to the server via ShadowProxy and pickles the params passed to proxies build method
    necessary to instantiate the ShadowBot
    """

    shell("python build.py")


@Shadow.command()
@click.argument("name")
def retract(name):
    """Removes ShadowBot from the server"""

    Core().retract(name)


# TODO - Bot Group


@Shadow.group()
def bot():
    """Bot communication"""
    pass


@bot.command()
@click.argument("name")
def start(name):
    """Starts the ShadowBot's process

    Args:
        name ([str]): Name of the ShadowBot to start
    """

    # TODO - Non-blocking start
    click.echo(
        "Once the bot is started, press ctrl-c to exit the start process. The ShadowBot will still be running (currently in my TODO list for non-blocking start up)"
    )

    Core().signal(name=name, event="start", task="")


@bot.command()
@click.argument("name")
def stop(name):
    click.echo("Not implemented yet")

    Core().signal(name=name, event="kill", task="")


@bot.command()
def alive():
    click.echo("Not implemented yet")


@bot.command()
def perform():
    click.echo("Not implemented yet")


@bot.command()
def wait():
    click.echo("Not implemented yet")


@bot.command()
def compile():
    click.echo("Not implemented yet")
