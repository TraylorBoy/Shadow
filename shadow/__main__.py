"""Command line script for the Shadow package"""

from loguru import logger

from shadow.bot import ShadowBot
from shadow.observer import ShadowObserver
from shadow.task import ShadowTask


@logger.catch
def main():
    """Provides a command interface for interacting with the Shadow package"""

    task_list = ShadowTask()

    def truth():
        return True

    def sleep(len: int = 3):
        import time

        time.sleep(len)
        return True

    task_list.add(name="truth", task=truth)
    task_list.add(name="sleep", task=sleep, len=1)

    bot = ShadowBot(name="TestBot", shadow_task=task_list)
    bot.register(observer=ShadowObserver())

    with bot:
        bot.requests.put("truth")
        bot.requests.put("sleep")

        print(bot.responses.get())
        print(bot.responses.get())


if __name__ == "__main__":
    """Entry point"""

    main()
