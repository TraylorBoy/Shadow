"""Creates a network of ShadowBots"""

import sys
import asyncio
import dill

from datetime import datetime

from functools import partial

from typing import Optional, Any, Dict, Callable, List

from shadow.helpers import Borg
from shadow.interface import IShadowNetwork
from shadow.bot import ShadowBot
from shadow.needles import Needles

from loguru import logger

def network_log(record):
    return record["name"] in ["shadow.network", "shadow.needles", "shadow.bot", "shadow.clone"]

# Setup log file
logger.add(
    f"shadow/logs/server/{datetime.now().month}_{datetime.now().day}_{datetime.now().year}.log",
    rotation="500 MB",
    enqueue=True,
    filter=network_log
)

class ShadowNetwork(Borg, IShadowNetwork):

    """Manages ShadowBots and the server"""

    def __init__(self, host: str = "127.0.0.1", port: int = 8888):
        """Initializes shared state and properties between each instance

        Args:
            host (str, optional): Host to run server on. Defaults to "127.0.0.1".
            port (int, optional): Port to connect to. Defaults to 8888.
        """

        super().__init__()

        if not hasattr(self, "host"):
            self.host: str = host

        if not hasattr(self, "port"):
            self.port: int = port

        if not hasattr(self, "server"):
            self.server: Optional[asyncio.Server] = None

        if not hasattr(self, "needles"):
            self.needles: Needles = Needles()

# --------------------------------- Interface -------------------------------- #

    async def serve(self):
        """Start running server
        """

        logger.info(f"Serving on {self.host}:{self.port}")

        await self.create_server()

        async with self.server:

            try:

                await self.server.serve_forever()

            except Exception:
                pass

    async def send(self, message: Dict[str, Optional[Any]]):
        """Sends a message to the server

        Args:
            message (Dict[str, Optional[Any]): Message to send to the server

        Returns:
            [Dict[str, Optional[Any]]]: Response received from server
        """

        reader, writer = await asyncio.open_connection(self.host, self.port)

        writer.write(dill.dumps(message))
        await writer.drain()

        # Close stream
        if writer.can_write_eof():
            writer.write_eof()

        data: Optional[Any] = await self.read(reader)

        if data:
            # Close connection
            writer.close()
            await writer.wait_closed()

            response: Optional[Any] = dill.loads(b"".join(data))

            # Return response
            return response

    async def kill(self):
        """Sends a kill event to the server
        """

        message: Dict[str, Optional[Any]] = {"event": "kill", "data": None}

        await self.send(message)

    async def build(self, name: str, tasks: Dict[str, partial]):
        """Build wrapper for proxy

        Args:
            name (str): Name to identify the ShadowBot on the network
            tasks (Dict[str, partial]): Tasks for the ShadowBot to perform
        """

        message: Dict[str, Optional[Any]] = {

            "event": "build",
            "data": {"name": name, "tasks": tasks}

        }

        await self.send(message)

# ---------------------------------- Network --------------------------------- #

    async def create_server(self):
        """Creates an asyncio.Server instance
        """

        self.server = await asyncio.start_server(self.receive, self.host, self.port, start_serving=False)

    async def write(self, response: Dict[str, Optional[Any]], writer: asyncio.StreamWriter):
        """Sends a response to the client and cleans up the StreamWriter

        Args:
            response (Dict[str, Optional[Any]]): Data to send to the client
            writer (asyncio.StreamWriter): Client write socket
        """

        logger.info(f"Sending a response: {response}")

        writer.write(dill.dumps(response))
        await writer.drain()

        if writer.can_write_eof():
            writer.write_eof()

            logger.success("Response sent")

    async def read(self, reader: asyncio.StreamReader):
        """Reads data sent to the server

        Args:
            reader (asyncio.StreamReader): Read socket

        Returns:
            [Optional[Any]]: Data sent to the server
        """

        data: List[Any] = []

        while True:
            packet = await reader.readline()
            if not packet: break
            data.append(packet)

        return data

    async def receive(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Client connection calllback for when server starts running

        Args:
            reader (asyncio.StreamReader): Read socket
            writer (asyncio.StreamWriter): Write socket
        """

        data: Optional[Any] = await self.read(reader)

        if data:

            message: Dict[str, Optional[Any]] = dill.loads(b"".join(data))

            logger.info(f"Received message: {message}")

            try:

                await self.process(message, writer)

            except SystemExit:
                logger.warning("Shutting down server")
                self.server.close()

            except Exception as e: # pragma: no cover
                logger.exception(e)

            finally:

                writer.close()
                await writer.wait_closed()

            logger.success("Message processed successfully")

    async def process(self, message: Dict[str, Optional[Any]], writer: asyncio.StreamWriter):
        """Processes data sent to the server

        Args:
            message (Dict[str, Optional[Any]]): Data sent from the client,
            writer (asyncio.StreamWriter): Write socket
        """

        logger.debug(f"Processing message: {message}")

        handlers: Dict[str, Callable] = {
            "kill": self.__stop,
            "status": self.__status,
            "build": self.__build,
            "retract": self.__retract,
        }

        if message["event"] in handlers.keys():

            event: str = message["event"]
            _params: Optional[Any] = message["data"]

            if _params is not None:
                await handlers[event](writer, **_params)
            else:
                await handlers[event](writer)

        else:
            logger.warning(f"Invalid event received: {message['event']}")

    async def __stop(self, writer: asyncio.StreamWriter):
        """Kill message event handler
        """

        response: Dict[str, Optional[Any]]= {
            "event": "kill",
            "data": "Shutting down"
        }

        await self.write(response, writer)

        sys.exit()

    async def __status(self, writer: asyncio.StreamWriter):
        """Status message handler

        Args:
            writer (asyncio.StreamWriter): Send socket
        """

        logger.info("Server Status: Alive")
        logger.info(f"Needles Status: {self.needles}")

        response: Dict[str, Optional[Any]] = {
            "event": "status",
            "data": {"server": "Alive", "needles": list(self.needles.needles.keys())}
        }

        await self.write(response, writer)

    async def __build(self, writer: asyncio.StreamWriter, name: str, tasks: Dict[str, partial]):
        """Builds a ShadowBot and sews it on the ShadowNetwork

        Args:
            name (str): Name to identify the ShadowBot on the network
            tasks (Dict[str, partial]): Tasks for the ShadowBot to perform
        """


        logger.info(f"Building ShadowBot: {name}")
        shadowbot: ShadowBot = ShadowBot(name, tasks)

        logger.success("ShadowBot created, sewing")

        self.needles.sew(bot=shadowbot)

        response: Dict[str, Optional[Any]] = {
            "event": "build",
            "data": shadowbot.id
        }

        await self.write(response, writer)

    async def __retract(self, writer: asyncio.StreamWriter, name: str):
        """Retract message handler

        Args:
            writer (asyncio.StreamWriter): Send socket
            name (str): Name used to identify the ShadowBot
        """

        if not self.needles.check(bot=self.needles.needles[name]):

            logger.warning(f"Invalid needle: {name}")

            return None

        logger.info(f"Retracting needle: {self.needles.needles[name]}")

        essence: Dict[str, Dict[str, partial]] = self.needles.retract(bot=self.needles.needles[name])

        logger.success(f"Needle retracted: {essence}")

        response: Dict[str, Optional[Any]] = {
            "event": "status",
            "data": {"needle": essence}
        }

        await self.write(response, writer)

    async def __start_up(self, writer: asyncio.StreamWriter, name: str):
        """Starts running the ShadowBot's process

        Args:
            writer (asyncio.StreamWriter): Write socket
            name (str): Name used to identify the ShadowBot
        """

        pass

    async def __signal(self, writer: asyncio.StreamWriter, event: str, data: Any):
        """Sends a signal to the running ShadowBot process

        Args:
            writer (asyncio.StreamWriter): Write socket
            event (str): Event to send to the process
            data (Any): Data associated with the event
        """

        pass
