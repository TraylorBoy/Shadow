from typing import Optional

from shadow.bot import ShadowBot

shadowbot: ShadowBot = ShadowBot()


def change_name(to: Optional[str] = None):

    shadowbot.rename(new_name=to)


def test_rename():

    assert shadowbot.name is None

    change_name(to="Rename Test")

    assert shadowbot.name == "Rename Test"
