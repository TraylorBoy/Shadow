"""Proxy to the ShadowNetwork interface"""

import socket
import dill

from functools import partial

from datetime import datetime

from typing import Any, Dict, Optional, Tuple

from shadow.core.interface import IShadowNetwork, IShadowBot
from shadow.core.network import ShadowNetwork
from shadow.core.bot import ShadowBot

from loguru import logger

def client_log(record):
    return record["name"] in ["shadow.client", "shadow.core"]

# Setup log file
logger.add(
    f"shadow/logs/client/{datetime.now().month}_{datetime.now().day}_{datetime.now().year}.log",
    rotation="500 MB",
    enqueue=True,
    filter=client_log
)

class ShadowNetworkProxy(IShadowNetwork):

    """ShadowNetwork Proxy class"""

    def __init__(self, host: str = "127.0.0.1", port: int = 0):
        """Instantiates the shadow network instance

        Args:
            host (str, optional): Host the server is running on. Defaults to "127.0.0.1".
            port (int, optional): Port the server is listening on. Defaults to 0.
        """

        self.network: ShadowNetwork = ShadowNetwork(host, port)
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def __del__(self):
        """Clean up
        """

        self.sock.close()

    def serve(self):
        """Start running the server instance on a seperate thread
        """

        self.network.run_server()

    def kill(self):
        """Stops the running server instance
        """

        self.network.stop_server()
        self.sock.close()

    def send(self, message: Tuple[str, Optional[Any]]):
        """Sends a message to the running server instance

        Args:
            message (Tuple[str, Optional[Any]]): Message to send to the server

        Returns:
            [Optional[Tuple[str, Optional[Any]]]]: Response received from the server
        """

        self.sock.sendall(dill.dumps(message))

        return dill.loads(self.sock.recv(1024))

    def alive(self):
        """Checks if network is running

        Returns:
            [bool]: Network is alive
        """

        return self.network.alive()

    def build(self, name: str, tasks: Dict[str, partial]):
        """Builds a ShadowBot on the network

        Args:
            name (str): [description]
            tasks (Dict[str, partial]): [description]

        Returns:
            [Optional[Tuple[str, Optional[Any]]]: Response received from the server
        """

        data: Tuple[str, Dict[str, partial]] = (name, tasks)

        return self.send(message=("build", data))

class ShadowBotProxy(IShadowBot):

    """ShadowBot and ShadowClone proxy class"""

    def __init__(self, name: str, tasks: Dict[str, Optional[Any]]):
        """Set the proxies initial state

        Args:
            name (str): Name of the ShadowBot
            tasks (Dict[str, Optional[Any]]): Tasks that the ShadowBot should perform
        """

        self.bot: ShadowBot = ShadowBot(name, tasks)

    def alive(self):
        """Checks if ShadowBot process has started

        Returns:
            [bool]: Process is running or not
        """

        return self.bot.alive()

    def start(self):
        """Transitions state from off to on and starts the ShadowBot's process"""

        self.bot.start()

    def stop(self):
        """Stop the running ShadowBot process"""

        self.bot.stop()

    @logger.catch
    def request(self, type: str, task: Optional[str]):
        """Sends a request to the ShadowBot

        Args:
            type (str): Type of request to send
            task (Optional[str]): Task to send to the ShadowBot if the request type is "wait" or "perform"
        """

        self.bot.request(type, task)

    @logger.catch
    def response(self):
        """Check for a response from the ShadowBot

        Returns:
            [Optional[Tuple[str, any]]]: Result from the requested task
        """

        return self.bot.response()

    def wait(self, task: str):
        """Waits for task to complete

        Args:
            task (str): Task to wait for

        Returns:
            [Optional[Tuple[str, any]]]: Result from the waited task
        """

        self.request(type="wait", task=task)

        return self.response()

    def perform(self, task: str):
        """Performs the task specified

        Args:
            task (str): Task to be executed by the ShadowBot
        """

        self.request(type="perform", task=task)
