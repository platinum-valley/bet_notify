import pytest
from src.notify import Notifier


def test_generate_notifier():
    assert type(Notifier()) == Notifier
