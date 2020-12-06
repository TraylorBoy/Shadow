"""Command line script for the Shadow package"""

from loguru import logger

from shadow.core import Shadow

# TODO: Console Commands


@logger.catch
def main():
    """Provides a command interface for interacting with the Shadow package"""

    shadow = Shadow()

    shadowbot = shadow.make("TestBot")

    logger.info(f"Created ShadowBot: {shadowbot.name}")

    logger.info("Turning the ShadowBot on")

    shadowbot.activate()

    logger.info("Turning the ShadowBot off")

    shadowbot.deactivate()


if __name__ == "__main__":
    """Entry point"""

    main()
