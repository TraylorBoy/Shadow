"""Command line script for the Shadow package"""

from loguru import logger

from shadow.core import Shadow

# TODO: Console Commands

if __name__ == "__main__":
    """Entry point"""

    try:
        shadow = Shadow()

        shadowbot = shadow.make("TestBot")

        logger.info(f"Created ShadowBot: {shadowbot.name}")

    except Exception as e:

        logger.exception(e)
