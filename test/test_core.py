from typing import Optional

from shadow.bot import ShadowBot
from shadow.core import Shadow


def make_shadowbot(name: Optional[str] = None) -> ShadowBot:

    shadow = Shadow()

    shadowbot = shadow.make(name=name)

    return shadowbot


def test_make() -> None:

    assert make_shadowbot().name is None
    assert make_shadowbot(name="TestBot").name == "TestBot"
