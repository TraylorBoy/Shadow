"""Command line script for the Shadow package"""

from shadow import Shadow

from loguru import logger

@logger.catch
def main():
    """Provides a command interface for interacting with the Shadow package"""

    Shadow()

if __name__ == "__main__":
    """Entry point"""

    main()
