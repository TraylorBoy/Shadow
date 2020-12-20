"""Pickling decoraters work-around"""

import functools
from typing import Callable


class ShadowCatch(object):

    """Function wrapper for pickling"""

    def __init__(self, target: Callable):
        """Set target function to wrap

        Args:
            target (Callable): Function to wrap for pickling
        """

        self.target: Callable = target

        # Update decorator with target
        functools.update_wrapper(self, target)

    def __call__(self, target):
        """Call wrapped function

        Args:
            target ([type]): Decorated function being called

        Returns:
            [type]: Wrapped function instance
        """

        target.func = target

        return target
