"""Command line application for the Shadow project"""

import os
import click
import dill

from shell import shell

from typing import Optional, Tuple, Any, Dict

from shadow import ShadowProxy, Needles

class Core(object):

    """Application entry point"""

    def __init__(self):
        """Setup the interactive console"""

        self.proxy: Optional[ShadowProxy] = None
        self.settings: Optional[Tuple[str, int]] = None

        self.load()

    def load(self):
        """Loads settings from cache
        """

        if os.path.exists("shadow/data/cache/connection.cache"):
            with open("shadow/data/cache/connection.cache", "rb") as cache_file:
                self.settings: Optional[Tuple[str, int]] = dill.load(cache_file)

    def store(self, value: Any):
        """Caches value

        Args:
            value (Any): Value to cache
        """

        with open("shadow/data/cache/connection.cache", "wb") as cache_file:
            dill.dump(value, cache_file)

    def connect(proxy, *args, **kwargs):
        """Opens a connection to the server for the decorated function

        Args:
            proxy ([type]): [description]
        """

        def connection(self, *args, **kwargs):
            if self.settings is not None:
                host, port = self.settings
            else:
                host, port = "127.0.0.1", 8888

            self.proxy = ShadowProxy(host, port)

            proxy(self, *args, **kwargs)

        return connection

    def serve(self, host: str, port: int):
        """Starts running the server on the given host and port

        Args:
            host (str): Host to run server on
            port (int): Port to communicate with the server
        """

        self.proxy = ShadowProxy(host, port)

        self.store(value=(host, port))

        self.proxy.serve()

    @connect
    def send(self, message: Dict[str, Optional[Any]]):
        """[summary]

        Args:
            message (str): [description]
        """

        click.echo(self.proxy.send(message))

    @connect
    def kill(self):
        """[summary]
        """

        self.proxy.kill()

    def reset(self):
        """Removes settings from cache
        """

        click.echo("Restoring default settings...")

        os.remove("shadow/data/cache/connection.cache")

        # Remove stored ShadowBots
        Needles().reset()

        click.echo("Restored")

core: Core = Core()

@click.group()
def Shadow():
    pass

@Shadow.command()
@click.option("--host", default="127.0.0.1", help="Host to run server on")
@click.option("--port", default=8888, help="Port to server communicates on")
def serve(host, port):
    """Start the ShadowNetwork
    """

    core.serve(host, port)

@Shadow.command()
@click.option("--event", default="status", help="Event to signal to the server")
@click.option("--data", default=None, help="Data to send to the server")
def send(event, data):
    """Send a request to the server

    Args:
        event ([str]): Event to signal to the server
        data ([Any]): Data to send to the server
    """

    message: Dict[str, Optional[Any]] = {
        "event": event,
        "data": data
    }

    core.send(message)

@Shadow.command()
def kill():
    """Stops the server
    """

    core.kill()

@Shadow.command()
def reset():
    """Resets stored state
    """

    core.reset()

@Shadow.command()
def build():
    """Executes the build script in current directory

    The build script connects to the server via ShadowProxy and pickles the params passed to proxies build method
    necessary to instantiate the ShadowBot
    """

    shell("python build.py")

