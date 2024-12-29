import collections

import pytest

from tests.conftest import MockInsertOne


def mock_department_count(value: int = 0):
    MockDepartmentTable = collections.namedtuple(
        'MockDepartmentTable', ('count_documents',)
    )

    async def count_documents(*args, **kwargs):
        return value

    return {
        'departments': MockDepartmentTable(count_documents=count_documents)
    }


@pytest.fixture
def stub_departments_count_0():
    from sop_chatbot import session

    original_db = session.db
    session.db = mock_department_count(0)
    yield
    session.db = original_db


@pytest.fixture
def stub_departments_count_10000():
    from sop_chatbot import session

    original_db = session.db
    session.db = mock_department_count(10000)
    yield
    session.db = original_db


@pytest.fixture
def department_request():
    return {
        'name': 'Development Department',
        'description': 'A department focused on development',
    }


@pytest.fixture
def department(time_now):
    return {
        '_id': '676ef484daff5f784260b96f',
        'name': 'Development Department',
        'description': 'A department focused on development',
        'registration': '003.0001.001',
        'owner': '001.0001.000',
        'created_at': time_now,
        'updated_at': time_now,
        'company': '002.0001.001',
    }


@pytest.fixture
def department_object(department):
    from sop_chatbot.models.departments import Department

    return Department(**department, id=department['_id'])


def mock_department_creation(id: str):
    from bson import ObjectId

    async def insert_one(*args, **kwargs):
        return MockInsertOne(ObjectId(id))

    return insert_one


@pytest.fixture
def stub_department_creation(stub_departments_count_0):
    from sop_chatbot import session

    MockDepartmentTable = collections.namedtuple(
        'MockDepartmentTable', ('insert_one', 'count_documents')
    )
    original_db = session.db
    session.db['departments'] = MockDepartmentTable(
        insert_one=mock_department_creation('676ef484daff5f784260b96f'),
        count_documents=session.db['departments'].count_documents,
    )
    yield
    session.db = original_db


@pytest.fixture
def stub_department_find(department):
    from sop_chatbot import session

    MockDepartmentTable = collections.namedtuple(
        'MockDepartmentTable', ('find_one', 'delete_one')
    )

    async def find_one(*args, **kwargs):
        return department

    async def delete_one(*args, **kwargs):
        return None

    original_db = session.db
    session.db['departments'] = MockDepartmentTable(
        find_one=find_one, delete_one=delete_one
    )
    yield
    session.db = original_db
