"""Task object used to instantiate ShadowBot instances"""

from functools import partial
from typing import Callable, Dict

import dill

from shadow.cache import ShadowCache


class ShadowTask(object):

    """Task object used to instansiate ShadowBot"""

    def __repr__(self):
        """ShadowTask description

        Returns:
            [str]: Task items
        """

        task_list: str = ""

        for signal, task in self.tasks.items():
            task_list += f"{signal} - {task}\n"

        return task_list

    def __init__(self):
        """Set initial task list"""

        self.tasks: Dict[str, partial] = {}

    def add(self, name: str, task: Callable, *args, **kwargs):
        """Add signal, function partial, and arguments to task list

        Args:
            name (str): Signal to call task
            task (Callable): Function to call
        """

        _task: partial = partial(task, *args, **kwargs)

        if name not in self.tasks.keys():
            self.tasks[name] = _task

    def remove(self, name: str):
        """Remove task from task list

        Args:
            name (str): Signal used to call task
        """

        if name in self.tasks.keys():
            del self.tasks[name]

    def save(self, list_name: str):
        """Store task list in memory cache

        Args:
            list_name (str): Name of task list to store; used to retrieve task from cache
        """

        with ShadowCache() as cache:

            cache.store(key=list_name, value=dill.dumps(self.tasks))

    def load(self, list_name: str):
        """Retrieves task list from memory cache

        Args:
            list_name (str): Name of task list to retrieve
        """

        with ShadowCache() as cache:
            self.tasks = dill.loads(cache.retrieve(key=list_name))
