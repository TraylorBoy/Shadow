"""Command line application for the Shadow project"""

import os
import time
import click
import dill

from typing import Optional, Tuple, Any, Dict

from shadow import ShadowProxy

class Core(object):

    """Application entry point"""

    def __init__(self):
        """Setup the interactive console"""

        self.proxy: Optional[ShadowProxy] = None
        self.settings: Optional[Tuple[str, int]] = None

        self.load()

    def load(self):
        """[summary]

        Returns:
            [type]: [description]
        """

        if os.path.exists("shadow/data/cache/connection.cache"):
            with open("shadow/data/cache/connection.cache", "rb") as cache_file:
                self.settings: Optional[Tuple[str, int]] = dill.load(cache_file)

    def store(self, value: Any):
        """[summary]

        Args:
            key (str): [description]
            value (Any): [description]
        """

        with open("shadow/data/cache/connection.cache", "wb") as cache_file:
            dill.dump(value, cache_file)

    def connect(proxy, *args, **kwargs):
        """[summary]

        Args:
            proxy ([type]): [description]
        """

        def connection(self, *args, **kwargs):
            host, port = self.settings
            self.proxy = ShadowProxy(host, port)

            proxy(self, *args, **kwargs)

        return connection

    def serve(self, host: str, port: int):
        """[summary]

        Args:
            host (str): [description]
            port (int): [description]
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
    """[summary]
    """

    core.kill()
