import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from sop_chatbot.main import app

pytest_plugins = ['tests.fixtures.user_fixtures']


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def async_client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://localhost:8000/api',
        timeout=60,
    )


@pytest.fixture
def awaitable_none():
    async def _awaitable_none():
        return None

    return _awaitable_none


@pytest.fixture
def awaitable_true():
    async def _awaitable_true():
        return True

    return _awaitable_true


@pytest.fixture
def awaitable_false():
    async def _awaitable_false():
        return False

    return _awaitable_false


@pytest.fixture
def awaitable_empty_list():
    async def _awaitable_empty_list():
        return []

    return _awaitable_empty_list


@pytest.fixture
def awaitable_empty_dict():
    async def _awaitable_empty_dict():
        return {}

    return _awaitable_empty_dict


@pytest.fixture
def awaitable_empty_string():
    async def _awaitable_empty_string():
        return ''

    return _awaitable_empty_string


@pytest.fixture
def awaitable_empty_int():
    async def _awaitable_empty_int():
        return 0

    return _awaitable_empty_int
