from typing import Optional

from shadow.bot import ShadowBot
from shadow.core import Shadow


def make_shadowbot(name: Optional[str] = None):

    shadow: Shadow = Shadow()

    shadowbot: ShadowBot = shadow.make(name=name)

    return shadowbot


def test_make():

    assert make_shadowbot().name is None
    assert make_shadowbot(name="TestBot").name == "TestBot"
