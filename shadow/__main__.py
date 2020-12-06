"""Command line script for the Shadow package"""

from time import sleep

from loguru import logger

from shadow.clone import ShadowClone
from shadow.core import Shadow

# TODO: Remove test code and add console Commands


@logger.catch
def main():
    """Provides a command interface for interacting with the Shadow package"""

    # Test Code

    shadow = Shadow()

    shadowclone = ShadowClone()
    shadowclone_two = ShadowClone()

    def test_run():
        sleep(5)

    shadowclone.assign(func=test_run)
    shadowclone_two.assign(func=shadow.make, name="TestBot")

    shadowclone.perform()

    shadowclone_three = ShadowClone()
    shadowclone_three.assign(
        func=shadow.observe, bot=shadowclone_two.perform(block=True)
    )

    shadowbot = shadowclone_two.perform()

    shadowclone_three.perform(block=True)

    print(shadowbot)


if __name__ == "__main__":
    """Entry point"""

    main()
