import asyncio
import collections

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from sop_chatbot.main import app

pytest_plugins = [
    'tests.fixtures.user_fixtures',
    'tests.fixtures.company_fixtures',
    'tests.fixtures.department_fixtures',
    'tests.fixtures.mixins_fixtures',
]

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@pytest.fixture
def async_loop():
    return loop


@pytest.fixture(autouse=True)
def setup():
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo import MongoClient

    import sop_chatbot.session as session
    from sop_chatbot.config import settings

    def clear_db():
        db = settings.TEST_MONGO_URI.split('/')[-1]
        MongoClient(settings.TEST_MONGO_URI).drop_database(db)

    session.db = AsyncIOMotorClient(settings.TEST_MONGO_URI).get_database()
    clear_db()
    yield
    clear_db()


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


@pytest.fixture
def time_now():
    return '2024-12-27T18:43:19.339384'


MockInsertOne = collections.namedtuple('MockInsertOne', ('inserted_id',))
