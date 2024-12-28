import pytest
import time_machine

from sop_chatbot.services.auth import Auth


@pytest.fixture
def token(time_now):
    with time_machine.travel(time_now, tick=False):
        return Auth.generate_jwt('001.0001.000')
