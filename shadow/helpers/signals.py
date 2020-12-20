"""Collection of signals and tasks that the ShadowBot can run"""

import time
from typing import Callable, Dict

# ---------------------------------------------------------------------------- #
#                                 Test signals                                 #
# ---------------------------------------------------------------------------- #


def true_test():
    """Only returns True, mainly used for testing"""

    return True


def sleep_test(length: int = 1):
    """Have process sleep for length seconds

    Args:
        length (int): Length process should sleep for
    """

    time.sleep(length)

    return True


TEST_SIGNALS: Dict[str, Callable] = {"true": true_test, "sleep": sleep_test}
