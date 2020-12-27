"""Build ShadowBots"""

import random

from shadow import ShadowProxy
from shadow.helpers import Tasks

from loguru import logger

@logger.catch
def main():
    """Entry Point
    """

    logger.info("Building ShadowBot")

    proxy: ShadowProxy = ShadowProxy(host="127.0.0.1", port=8888)
    proxy.build(name="Test" + str(random.randint(1, 3)) + "Bot", tasks=Tasks["test"])

    logger.success("ShadowBot created")

if __name__ == '__main__':
    main()
