"""Command line script for the Shadow package"""

from loguru import logger

from shadow.core import Shadow


@logger.catch
def main():
    """Provides a command interface for interacting with the Shadow package"""

    shadow = Shadow()

    shadow.start()


if __name__ == "__main__":
    """Entry point"""

    main()
