"""Command line script for the Shadow package"""

import time

from loguru import logger

from shadow.core import Shadow

# TODO: Remove test code and add console Commands

shadow = Shadow()

@logger.catch
def main():
    """Provides a command interface for interacting with the Shadow package"""

    pass

if __name__ == "__main__":
    """Entry point"""

    main()
