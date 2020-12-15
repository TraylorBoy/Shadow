"""Command line script for the Shadow package"""

import time

from loguru import logger

from shadow.core import Shadow

# TODO: Remove test code and add console Commands
shadow = Shadow()


def say_hi():
    print("Hi")
    return True


def sleep():
    time.sleep(1)
    print("Good morning")
    return True


def test_bot():
    # test_bot_two()

    shadowbot = shadow.build(name="TestBot")
    shadow.observe(bot=shadowbot)
    shadowbot.add_task(signal="hi", task=say_hi)
    shadowbot.perform_task(signal="hi", wait=False)

    test_bot_two()


def test_bot_two():
    shadowbot_two = shadow.build(name="TestBot")
    shadow.observe(bot=shadowbot_two)
    shadowbot_two.add_task(signal="sleep", task=sleep)
    shadowbot_two.perform_task(signal="sleep", wait=True)


@logger.catch
def main():
    """Provides a command interface for interacting with the Shadow package"""

    # Test Code

    test_bot()


if __name__ == "__main__":
    """Entry point"""

    main()
