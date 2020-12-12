"""Command line script for the Shadow package"""

from loguru import logger

from shadow.core import Shadow

# TODO: Remove test code and add console Commands


def say_hi():
    print("Hi")


@logger.catch
def main():
    """Provides a command interface for interacting with the Shadow package"""

    # Test Code

    shadow = Shadow()

    shadowbot = shadow.make(name="TestBot")
    shadowbot.add_task(signal="hi", task=say_hi)

    shadow.observe(bot=shadowbot)

    shadowbot.start()

    shadowbot.messages.put(("history", True))
    hist = shadowbot.results.get()
    logger.debug(f"History retrieved: {hist}")
    shadowbot.stop()


if __name__ == "__main__":
    """Entry point"""

    main()
