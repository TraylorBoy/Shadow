"""Creates a network of ShadowBots"""

from datetime import datetime

from functools import partial
from typing import Optional, Any, Dict, Tuple

from .interface import IShadowNetwork
from .client import ShadowClient
from shadow.core.helpers import Borg
from shadow.server import ShadowServer
from shadow.core.bot.proxy import ShadowBotProxy
from shadow.core.bot.needle import Needle

from loguru import logger

def network_log(record):
    return record["name"] in ["shadow.server"]

# Setup log file
logger.add(
    f"shadow/logs/server/{datetime.now().month}_{datetime.now().day}_{datetime.now().year}.log",
    rotation="500 MB",
    enqueue=True,
    filter=network_log
)

class ShadowNetwork(Borg, IShadowNetwork):

    """Manages ShadowBots and the server"""

    def __init__(self, host: str = "127.0.0.1", port: int = 0):
        """Initializes shared state and properties between each instance

        Args:
            host (str, optional): Host to run server on. Defaults to "127.0.0.1".
            port (int, optional): Port to connect to. Defaults to 0.
        """

        self.__setup(host, port)

    def __setup(self, host: str, port: int): # pragma: no cover
        """Setup singleton instance
        """

        super().__init__()

        if not hasattr(self, "host"): self.host: str = host
        if not hasattr(self, "port"): self.port: int = port
        if not hasattr(self, "server"): self.server: ShadowServer = ShadowServer(self.host, self.port)
        if not hasattr(self, "server_bot"): self.__setup_server_bot()

    def __setup_server_bot(self):
        """Creates a ShadowBot that manages the servers tasks
        """

        server_tasks: Dict[str, partial] = {
            "serve": partial(self.server.serve),
            "shutdown": partial(self.stop)
        }

        essence: Needle = Needle(name="ServerBot", tasks=server_tasks, history={})
        self.server_bot: ShadowBotProxy = ShadowBotProxy(essence)
        self.server_bot.keep_alive = True

# --------------------------------- Interface -------------------------------- #

    @logger.catch
    def serve(self):
        """Start serving with the ServerBot

        Returns
            [bool]: ServerBot is alive or not
        """

        with self.server_bot:
            self.server_bot.perform(task="serve")

        return self.alive()

    @logger.catch
    def kill(self):
        """Stop serving with the ServerBot

        Returns
            [bool]: Server shutdown response
        """

        if not self.alive():
            logger.critical("ServerBot is not alive")
            return None

        resp: Optional[Any] = None
        with self.server_bot:
            resp = self.server_bot.jutsu(task="shutdown")
            self.server_bot.keep_alive = False

        return resp

    @logger.catch
    def alive(self):
        """Checks if ServerBot is alive

        Returns
            [bool]: ServerBot is alive or not
        """

        return self.server_bot.alive()

    @logger.catch
    def request(self, event: str, data: Optional[Any] = None):
        """Sends a request to the server

        Args:
            event (str): Event to send
            data (Optional[Any]): Data associated with the request. Defaults to None.

        Returns:
            [Optional[Any]]: Response from the server
        """

        if not self.alive():
            logger.critical("ServerBot is not alive")
            return None

        message: Tuple[str, Optional[Any]] = (event, data)
        resp: Tuple[str, Optional[Any]] = self.client.send(message)

        return resp

# ----------------------------------- Core ----------------------------------- #

    @property
    def client(self):
        """Client connection to the server

        Returns:
            [ShadowClient]: Instantiated client object
        """

        return ShadowClient(self.host, self.port)

    @logger.catch
    def stop(self):
        """Sends a shutdown signal to the server

        Returns:
            [Optional[Tuple[str, Optional[Any]]]]: Response from the server
        """

        if not self.alive():
            logger.critical("ServerBot is not alive")
            return None

        logger.debug("Sending shutdown request to server")

        return self.client.send(message=("shutdown", None))
