import collections
from datetime import datetime
from enum import Enum

import pytest
from bson import ObjectId

from sop_chatbot.models import mixins
from sop_chatbot.models.mixins import BaseClass, BaseRequest
from tests.conftest import MockInsertOne


@pytest.fixture
def MockRequest():
    class Request(BaseRequest):
        company: str

    return Request


@pytest.fixture
def MockClass():
    class Mock(BaseClass):
        @classmethod
        async def gen_registration(cls, owner, **kwargs):
            return await super().gen_registration(owner, **kwargs)

    return Mock


@pytest.fixture
def MockEnum():
    class MockEnum(Enum):
        value = 'mock'

    return MockEnum


@pytest.fixture
def mock_dict(time_now):
    return {
        '_id': ObjectId('676ff4ea01892d16d07c41b4'),
        'registration': '000.0000.000',
        'created_at': datetime.fromisoformat(time_now),
        'updated_at': datetime.fromisoformat(time_now),
        'owner': '001.0000.000',
        'company': '002.0000.000',
    }


@pytest.fixture
def mock_object(MockClass, mock_dict):
    return MockClass(id=str(mock_dict['_id']), **mock_dict)


@pytest.fixture
def ComplexMockClass(MockClass, MockEnum, mock_object):
    class ComplexMock(MockClass):
        workspace_id: str = '676ff4ea01892d16d07c41b4'
        composed_class: MockClass = mock_object  # type: ignore
        composed_enum: MockEnum = MockEnum.value  # type: ignore
        composed_array: list = [1, 2, 3]

    return ComplexMock


@pytest.fixture
def complex_mock_object(mock_object, ComplexMockClass):
    return ComplexMockClass(**mock_object.model_dump())


@pytest.fixture
def stub_update_mock_object():
    from sop_chatbot import session

    async def _stub_update_mock_object(*args, **kwargs):
        return None

    MockUpdateTable = collections.namedtuple('MockUpdateTable', ['update_one'])

    original_db = session.db
    session.db = {'mocks': MockUpdateTable(_stub_update_mock_object)}
    yield
    session.db = original_db


def mock_mock_count(value: int = 0):
    MockMockTable = collections.namedtuple(
        'MockMockTable', ('count_documents',)
    )

    async def count_documents(*args, **kwargs):
        return value

    return {'mocks': MockMockTable(count_documents=count_documents)}


@pytest.fixture
def stub_mocks_count_0(MockClass):
    from sop_chatbot import session

    original_db = session.db
    session.db = mock_mock_count(0)
    mixins.CLASS_MAPPING['Mock'] = '000'
    yield
    session.db = original_db
    del mixins.CLASS_MAPPING['Mock']


def mock_mock_creation(id: str):
    from bson import ObjectId

    async def insert_one(*args, **kwargs):
        return MockInsertOne(ObjectId(id))

    return insert_one


@pytest.fixture
def stub_create_mock_object(monkeypatch: pytest.MonkeyPatch):
    from sop_chatbot import session

    async def _gen_registration(owner):
        return '000.0000.000'

    monkeypatch.setattr(
        'sop_chatbot.models.mixins.BaseClass.gen_registration',
        _gen_registration,
    )

    MockMockTable = collections.namedtuple('MockMockTable', ('insert_one',))

    original_db = session.db
    session.db = {
        'mocks': MockMockTable(
            insert_one=mock_mock_creation('676ff4ea01892d16d07c41b4')
        )
    }
    yield
    session.db = original_db


@pytest.fixture
def stub_find_one_mock_object(mock_dict):
    from sop_chatbot import session

    async def find_one(*args, **kwargs):
        return mock_dict

    MockTable = collections.namedtuple('MockTable', ('find_one',))
    stub = MockTable(find_one=find_one)
    original_db = session.db
    session.db = {'mocks': stub}
    yield
    session.db = original_db


@pytest.fixture
def stub_find_all_mocks(stub_find_user_user, mock_dict):
    from sop_chatbot import session

    Limit = collections.namedtuple('Limit', ('limit',))

    async def limit(*args, **kwargs):
        yield mock_dict

    Skip = collections.namedtuple('Skip', ('skip',))

    def skip(*args, **kwargs):
        return Limit(limit=limit)

    def find(*args, **kwargs):
        return Skip(skip=skip)

    async def _count_documents(*args, **kwargs):
        return 1

    MockTable = collections.namedtuple(
        'MockTable', ('find', 'count_documents')
    )
    stub = MockTable(find=find, count_documents=_count_documents)
    original_db = session.db
    session.db = {'mocks': stub, 'users': session.db['users']}
    yield
    session.db = original_db


@pytest.fixture
def stub_delete_mock_object():
    from sop_chatbot import session

    async def _delete_mock_object(*args, **kwargs):
        return None

    MockDeleteTable = collections.namedtuple('MockDeleteTable', ['delete_one'])

    original_db = session.db
    session.db = {'mocks': MockDeleteTable(_delete_mock_object)}
    yield
    session.db = original_db
