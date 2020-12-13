import pytest

from shadow.observer import Observable, ShadowObserver


@pytest.fixture
def publisher():
    return Observable()


@pytest.fixture
def subscriber():
    return ShadowObserver()


def test_register(publisher, subscriber):

    publisher.register(observer=subscriber)
    assert subscriber in publisher.observers

    # Cover notify/update
    args = ["test"]
    kwarg = {"msg": "test"}
    publisher.notify(*args)
    publisher.notify(**kwarg)


def test_deregister(publisher, subscriber):

    publisher.deregister(observer=subscriber)
    assert subscriber not in publisher.observers
