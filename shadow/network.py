"""Creates a network of ShadowBots"""

import sys
import asyncio
import dill

from threading import Thread

from datetime import datetime

from functools import partial

from typing import Optional, Any, Dict, Callable, List, Tuple

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
            "sew": self.__sew,
            "retract": self.__retract,
            "signal": self.__signal
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

        response: Optional[Dict[str, Optional[Any]]] = None

        if data:

            response = dill.loads(b"".join(data))

            # Close connection
            writer.close()
            await writer.wait_closed()

        # Return response
        return response

    async def kill(self):
        """Sends a kill event to the server
        """

        message: Dict[str, Optional[Any]] = {"event": "kill", "data": None}

        return await self.send(message)

    async def sew(self, name: str, tasks: Dict[str, partial]):
        """Build wrapper for proxy

        Args:
            name (str): Name to identify the ShadowBot on the network
            tasks (Dict[str, partial]): Tasks for the ShadowBot to perform
        """

        message: Dict[str, Optional[Any]] = {

            "event": "sew",
            "data": {"name": name, "tasks": tasks}

        }

        return await self.send(message)

    async def retract(self, name: str):
        """Sends a message to the network to retract a sewn ShadowBot from the network

        Args:
            name (str): Name used to identify the ShadowBot
        """

        message: Dict[str, Optional[Any]] = {
            "event": "retract",
            "data": {
                "name": name
            }
        }

        return await self.send(message)

    async def signal(self, name: str, event: str, task: str):
        """Signals an event to ShadowBot on the network

        Args:
            name (str): Name used to identify the ShadowBot
            event (str): Event for ShadowBot to handle
            task (str): Task for ShadowBot to perform
        """

        logger.info(f"Sending {event} signal to ShadowBot: {name}")

        message: Dict[str, Optional[Any]] = {
            "event": "signal",
            "data": {
                "name": name,
                "event": event,
                "task": task
            }
        }

        return await self.send(message)


# --------------------------------- Handlers --------------------------------- #

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

    async def __sew(self, writer: asyncio.StreamWriter, name: str, tasks: Dict[str, partial]):
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

        if not self.needles.check(name):

            logger.warning(f"Invalid needle: {name}")

            return None

        shadowbot: ShadowBot = self.needles.get(name)

        logger.info(f"Retracting needle: {shadowbot}")

        essence: Dict[str, Dict[str, partial]] = self.needles.retract(bot=shadowbot)

        logger.success(f"Needle retracted: {essence}")

        response: Dict[str, Optional[Any]] = {
            "event": "status",
            "data": {"needle": essence}
        }

        await self.write(response, writer)

    async def __signal(self, writer: asyncio.StreamWriter, name: str, event: str, task: str):
        """Sends a signal to the running ShadowBot process

        Args:
            writer (asyncio.StreamWriter): Write socket
            name (str): Name used to identify the ShadowBot
            event (str): Event for ShadowBot to handle
            task (str): Task for ShadowBot to perform
        """

        if self.needles.check(name):
            logger.info(f"Sending signal to ShadowBot: {name}")

            shadowbot: ShadowBot = self.needles.get(name)

            # TODO - Move to Proxy
            # Event can be:
            # start - Start running ShadowBot process
            # kill - Stop running ShadowBot process
            # task - ShadowBot performs task, get - Get result from ShadowBot
            # wait - Wait for result from ShadowBot
            bot_handlers: Dict[str, Callable] = {
                "start": self.start_bot,
                "kill": None,
                "task": None,
                "get": None,
                "wait": None,
                "status": None
            }

            if event in bot_handlers.keys():
                if not shadowbot.alive() and event != "start":
                    # TODO - Send error response message
                    logger.critical(f"{name}: is Dead, please start the ShadowBot first")
                else:

                    response: Optional[Dict[str, Optional[Any]]] = bot_handlers[event](bot=shadowbot, )
                    await self.write(response, writer)

# ------------------------------- Bot Handlers ------------------------------- #

    # FUCK YEH
    async def control_bot(self, command: str):
        """Wraps signal in the form of a command

        Args:
            command (str): Command for the Bot to perform on the network
        """

        # Compile - Perform + Wait + Get = Result
        commands: List[str] = ["start", "kill", "status", "compile"]

        if command in commands:
            bot_handlers: Dict[str, Callable] = {
                "start": self.start_bot,
                "kill": self.stop_bot,
                "status": self.status_bot,
                "compile": self.comp
            }


            handle: Callable = bot_handlers[command]

    # TODO - Docstring
    async def link_bot(self, name: str):
        """[summary]

        Args:
            name (str): [description]

        Returns:
            [type]: [description]
        """


        if self.needles.check(name):
            return self.needles.get(name)

    # TODO - Test

    async def start_bot(self, bot: ShadowBot):
        """Starts running ShadowBot process on the network

        Args:
            bot (ShadowBot): ShadowBot to start
        """

        logger.info(f"Starting ShadowBot: {bot.id}")

        try:

            Thread(target=bot.start, daemon=True).start() if not bot.alive() else logger.warning(f"{bot.id} is already alive")

        except AssertionError:
            # Reset ShadowBot process
            bot.reset()
            Thread(target=bot.start, daemon=True).start()

        logger.success(f"{bot} is now running")

        return True

    async def stop_bot(self, bot: ShadowBot):


        logger.info(f"Killing ShadowBot: {bot.id}")

        # Send kill signal
        bot.pipe["event"].put("kill", block=True)

        if not bot.alive():
            logger.success(f"{bot.id}is Dead")

    async def status_bot(self, bot: ShadowBot):

        response: Dict[str, Optional[Any]] = {
            "event": "signal",
            "data": {"alive": shadowbot.alive()}
        }

        await self.write(response, writer)

    async def wait_bot(self, bot: ShadowBot):

        shadowbot: ShadowBot = bot

        # Put the task to wait for in queue
        shadowbot.pipe["wait"].put(task, block=True)

        # Signal ShadowBot to wait for task
        shadowbot.pipe["event"].put("wait", block=True)

    async def perform_bot(self, bot: ShadowBot, task: str):
        """Assigns a task for ShadowBot to perform

        Args:
            bot (ShadowBot): ShadowBot to perform the task
            task (str): Task to be executed on a seperate thread
        """

        bot.pipe["task"].put(task, block=True)

        bot.pipe["event"].put("task", block=True)

    async def compile_bot(self, bot: ShadowBot, task: str):
        """[summary]

        Args:
            bot (ShadowBot): [description]
        """

        logger.info(f"Retrieving result for task: {task}")

        # Have ShadowBot perform task, and wait for result
        bot.pipe["compile"].put(task, block=True)

        # Compile result
        result: Optional[Tuple[str, Optional[Any]]] = bot.compile()

        if result is not None:

            task_name, value = result

            logger.success(f"Sending compiled result: {task_name}: {value}")

            response: Dict[str, Optional[Any]] = {
                "event": "signal",
                "data": {"task": task_name, "result": value}
            }

            return response

        else:

            logger.info(f"Failed to compile result for {task}")

