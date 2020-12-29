"""Pre-written tasklists to instanstitate a ShadowBot object with"""


from functools import partial
from typing import Dict


def flip(var: bool = True):
    """Returns not var

    Args:
        var (bool): Boolean type to flip

    Returns:
        [bool]: Opposite of var
    """

    return not var


TEST: Dict[str, partial] = {"flip": partial(flip)}


Tasks: Dict[str, Dict[str, partial]] = {"test": TEST}
