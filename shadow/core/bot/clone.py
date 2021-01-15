"""Task worker thread class"""

from threading import Thread

from loguru import logger

from typing import Optional, Any, Dict, List

class ShadowClone(Thread):

    """Slave class for perfoming tasks on seperate threads for the ShadowBot instance"""

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
        """Thread.__init__ override"""

        # Make sure subclass has access to passed arguments
        super(ShadowClone, self).__init__(group=group, target=target, name=name)

        self.args: List[Any] = args
        self.kwargs: Dict[str, Any] = kwargs

    def run(self):
        """Thread.run() override"""

        task, pipe = self.args

        logger.debug(f"Performing task: {task}")

        result: Optional[Any] = task()

        logger.debug(f"Putting result into pipe: ({self.name}, {result}) -> {pipe}")

        pipe.put((self.name, result))

        logger.debug("Task completed, rejoining")
