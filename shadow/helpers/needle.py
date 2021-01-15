"""NamedTuple for building, storing and retrieving ShadowBots on the network"""

from functools import partial
from typing import Dict, Optional, NamedTuple, Any

class Needle(NamedTuple):

    """Named tuple for representing the ShadowBot's essence"""

    name: str
    tasks: Dict[str, partial]
    history: Dict[str, Optional[Any]]
