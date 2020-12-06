"""Command line script for the Shadow package"""

from loguru import logger

from shadow.core import Shadow

# TODO: Console Commands


@logger.catch
def main():
    """Provides a command interface for interacting with the Shadow package"""

    shadow = Shadow()

    shadowbot = shadow.make(name="TestBot")

    logger.info(f"Created ShadowBot: {shadowbot.name}")

    shadowobserver = shadow.observe(bot=shadowbot)

    logger.info(f"Observing {shadowbot.name}")

    shadowbot.activate()

    shadowbot.deactivate()

    logger.info(f"Unobserving {shadowbot.name}")

    shadow.unobserve(bot=shadowbot, observer=shadowobserver)

    shadowbot.activate()

    shadowbot.deactivate()


if __name__ == "__main__":
    """Entry point"""

    main()
