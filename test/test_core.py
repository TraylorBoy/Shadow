import pytest

import shadow


@pytest.fixture
def tasker():
    return shadow.ShadowTask()


def test_tasker(tasker):

    assert len(tasker.tasks) == 0
