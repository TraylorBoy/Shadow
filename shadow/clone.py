"""Worker class that performs tasks asynchronously"""

from copy import copy
from typing import Any, Callable, Optional, Tuple


class ShadowClone:

    """Task worker"""

    def __init__(self):
        """Set initial task"""

        self.task: Optional[Tuple] = None

    def assign(self, func: Callable, **kwargs):
        """Assigns a new task"""

        # Assign function and function args
        self.task = (func, kwargs)

    def perform(self):
        """Performs assigned task and returns result"""

        # TODO - Async

        result: Any = self.task[0](**self.task[1])

        return result

    def clone(self):
        """Prototype method for copying ShadowClones"""

        return copy(self)
