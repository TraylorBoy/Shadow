"""Build ShadowBots"""

import random

from datetime import datetime

from shadow import ShadowProxy
from shadow.helpers import Tasks

from loguru import logger

# Setup log file
logger.add(
    f"shadow/logs/client/{datetime.now().month}_{datetime.now().day}_{datetime.now().year}.log",
    rotation="500 MB",
    enqueue=True,
)

@logger.catch
def main():
    """Entry Point
    """

    logger.info("Building ShadowBot")

    proxy: ShadowProxy = ShadowProxy(host="127.0.0.1", port=8888)

    proxy.sew(name="TestBot - " + str(random.randint(1, 3)), tasks=Tasks["test"])

    logger.success("ShadowBot created")

if __name__ == '__main__':
    main()
