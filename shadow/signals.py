"""Collection of signals and tasks that the ShadowBot can run"""

import time
from typing import Callable, Dict

# ---------------------------------------------------------------------------- #
#                                 Test signals                                 #
# ---------------------------------------------------------------------------- #


def true_test():
    """Only returns True"""

    return True

def echo(*args, **kwargs):
    """Prints arguments to stdout
    """


    for arg in args:
        print(arg)

    for key, arg in kwargs.items():
        print(f"{key}: {arg}")

# ---------------------------------------------------------------------------- #
#                                Utility Signals                               #
# ---------------------------------------------------------------------------- #


def good_night(length: int = 1):
    """Have process sleep for length seconds

    Args:
        length (int): Length process should sleep for
    """

    time.sleep(length)

    return True


class ShadowSignal(object):

    """Reusable signals for the ShadowTask class"""

    UTILITIES: Dict[str, Callable] = {"sleep": good_night}

    TEST: Dict[str, Callable] = {"true": true_test, "echo": echo}
