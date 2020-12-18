"""Task object used to instantiate ShadowBot instances"""

from functools import partial
from typing import Callable, Dict


class ShadowTask(object):

    """Task object used to instansiate ShadowBot"""

    def __repr__(self):
        # Todo: Docstring

        task_list: str = ""

        for signal, task in self.tasks.items():
            task_list += f"{signal} - {task}\n"

        return task_list

    def __init__(self):
        """Set initial task list"""

        self.tasks: Dict[str, partial] = {}

    def add(self, name: str, task: Callable, *args, **kwargs):
        # Todo: Docstring

        task: partial = partial(task, *args, **kwargs)

        if name not in self.tasks.keys():
            self.tasks[name] = task

    def remove(self, name: str):
        # Todo: Docstring

        if name in self.tasks.keys():
            task: partial = self.tasks[name]
            del self.tasks[name]

    def save(self, list_name: str):
        # Todo: Docstring

        # Todo: Store tasks in cache server
        pass

    def load(self, list_name: str):
        # Todo: Docstring

        # Todo: Load task from cache server
        pass
