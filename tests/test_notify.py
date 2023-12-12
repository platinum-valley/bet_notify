import pytest
from src.notify import Notifier


def test_generate_notifier():
    assert type(Notifier()) == Notifier


def test_has_message():
    message = "hogehoge"
    assert Notifier(message).message == message


def test_has_message_2():
    message = "burabura"
    assert Notifier(message).message == message
