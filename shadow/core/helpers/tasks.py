"""Pre-written tasks to instanstitate a ShadowBot object with"""

import time

from functools import partial
from typing import Dict, Union

def goodnight(sleep_for: int = 1):
    """Sleeps for a specified time in seconds

    Args:
        sleep_for (int, optional): Specified time to sleep for. Defaults to 1.

    Returns:
        [bool]: True if the sleep was successful
    """

    time.sleep(sleep_for)

    return True

def args_sum(*args):
    """Calculates the sum of the values

    Returns:
        [Union[int, float]]: The sum of the values passed in
    """

    ans: Union[int, float] = 0

    for num in args:
        ans += num

    return ans

FACTORY: Dict[str, partial] = {"sleep": goodnight, "sum": args_sum}

class Tasks(object):

    """Abstract Task factory
    """

    @staticmethod
    def get(task: str, *args, **kwargs):
        """Checks task factory for a given task

        Args:
            task (str): Task to retrieve from factory

        Returns:
            [partial]: Task wrapped as a partial
        """

        if task not in FACTORY.keys():
            return None

        # Create task as a partial
        task: partial = partial(FACTORY[task], *args, **kwargs)

        return task
