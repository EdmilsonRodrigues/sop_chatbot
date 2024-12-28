from datetime import datetime, timedelta

import time_machine

from sop_chatbot.services.auth import Auth


def test_generate_jwt():
    assert Auth.generate_jwt('001.0001.000')


def test_decode_jwt(token, time_now):
    result = {
        'sub': '001.0001.000',
        'exp': round(
            (
                datetime.fromisoformat('2024-12-27T18:43:19.339384')
                + timedelta(days=7)
            ).timestamp(),
            0,
        ),
    }

    payload = Auth.decode_jwt(token)

    assert payload == result


def test_decode_jwt_expired(token, time_now):
    with time_machine.travel('2025-12-28T18:43:19.339384', tick=False):
        assert Auth.decode_jwt(token) is None


def test_decode_invalid_jwt():
    assert Auth.decode_jwt('invalid_token') is None


def test_encrypt_password():
    assert Auth.encrypt_password('password')


def test_verify_password():
    hashed_password = Auth.encrypt_password('password')

    assert Auth.verify_password('password', hashed_password)
