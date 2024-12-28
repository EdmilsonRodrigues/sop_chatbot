import collections

import pytest

from sop_chatbot.models.mixins import CLASS_MAPPING


@pytest.fixture
def admin_request():
    return {
        'email': 'planetaedevelopment@gmail.com',
        'company_name': 'Planetae Development',
        'company_description': ' '.join(
            (
                'A company focused on developing high',
                'quality business automations and webapplications.',
            ),
        ),
        'name': 'Edmilson Monteiro Rodrigues Neto',
        'password': 'This is not my real password',
    }


@pytest.fixture
def user_request():
    return {
        'name': 'Edmilson Monteiro Rodrigues Neto',
        'password': 'This is not my real password',
        'role': 'user',
        'company': '002.0001.000',
        'departments': ['003.0001.000'],
    }


@pytest.fixture
def admin(admin_request):
    admin_request['role'] = 'admin'
    admin_request['departments'] = ['003.0001.000']
    admin_request['registration'] = '001.0001.000'
    admin_request['company'] = '002.0001.000'
    admin_request['_id'] = '676ef484daff5f784260b96e'
    admin_request['created_at'] = '2024-12-27T18:43:19.339384'
    admin_request['updated_at'] = '2024-12-27T18:43:19.339384'
    admin_request['owner'] = '001.0001.000'
    return admin_request


@pytest.fixture
def user(user_request):
    user_request['registration'] = '001.0001.001'
    user_request['_id'] = '676ef484daff5f784260b96f'
    user_request['created_at'] = '2024-12-27T18:43:19.339384'
    user_request['updated_at'] = '2024-12-27T18:43:19.339384'
    user_request['owner'] = '001.0001.000'
    return user_request


@pytest.fixture
def admin_object(admin):
    from sop_chatbot.models.users import Admin

    return Admin(**admin, id=admin['_id'])


@pytest.fixture
def user_object(user):
    from sop_chatbot.models.users import User

    return User(**user, id=user['_id'])


def mock_user_creation(id: str):
    from bson import ObjectId

    MockInsertOne = collections.namedtuple('MockInsertOne', ('inserted_id',))

    async def insert_one(*args, **kwargs):
        return MockInsertOne(ObjectId(id))

    return insert_one


@pytest.fixture
def stub_user_creation(user, stub_users_count_0):
    from sop_chatbot import session

    MockUserTable = collections.namedtuple(
        'MockUserTable', ('insert_one', 'aggregate')
    )
    original_db = session.db
    session.db['users'] = MockUserTable(
        insert_one=mock_user_creation(user['_id']),
        aggregate=session.db['users'].aggregate,
    )
    yield
    session.db = original_db


@pytest.fixture
def stub_admin_creation(admin, stub_admin_count_0, monkeypatch):
    from sop_chatbot import session

    MockUserTable = collections.namedtuple(
        'MockUserTable', ('insert_one', 'count_documents')
    )
    original_db = session.db
    session.db['users'] = MockUserTable(
        insert_one=mock_user_creation(admin['_id']),
        count_documents=session.db['users'].count_documents,
    )

    Company = collections.namedtuple('Company', ('registration', 'owner'))
    company_registration = '.'.join(
        (CLASS_MAPPING['Company'], admin['registration'].split('.')[1], '001')
    )

    async def _company(*args, **kwargs):
        return Company(company_registration, admin['registration'])

    monkeypatch.setattr(
        'sop_chatbot.models.companies.Company.create', _company
    )

    Department = collections.namedtuple('Department', ('registration'))
    department_registration = '.'.join(
        (
            CLASS_MAPPING['Department'],
            admin['registration'].split('.')[1],
            '001',
        )
    )

    async def _department(*args, **kwargs):
        return Department(department_registration)

    monkeypatch.setattr(
        'sop_chatbot.models.departments.Department.create', _department
    )
    yield
    session.db = original_db


def mock_find_user(value: dict | None = None):
    MockUserTable = collections.namedtuple('MockUserTable', ('find_one',))

    async def find_one(*args, **kwargs):
        return value

    return {'users': MockUserTable(find_one=find_one)}


@pytest.fixture
def stub_find_user_none():
    from sop_chatbot import session

    original_db = session.db
    session.db = mock_find_user()
    yield
    session.db = original_db


@pytest.fixture
def stub_find_user_user(user):
    from sop_chatbot import session

    original_db = session.db
    session.db = mock_find_user(user)
    yield
    session.db = original_db


@pytest.fixture
def stub_find_user_admin(admin):
    from sop_chatbot import session

    original_db = session.db
    session.db = mock_find_user(admin)
    yield
    session.db = original_db


def mock_admin_count(value: int = 0):
    MockUserTable = collections.namedtuple(
        'MockUserTable', ('count_documents',)
    )

    async def count_documents(*args, **kwargs):
        return value

    return {'users': MockUserTable(count_documents=count_documents)}


@pytest.fixture
def stub_admin_count_0():
    from sop_chatbot import session

    original_db = session.db
    session.db = mock_admin_count(0)
    yield
    session.db = original_db


@pytest.fixture
def stub_admin_count_10000():
    from sop_chatbot import session

    original_db = session.db
    session.db = mock_admin_count(10000)
    yield
    session.db = original_db


def mock_users_count(value: int = 0):
    MockUserTable = collections.namedtuple('MockUserTable', ('aggregate',))
    MockAggregate = collections.namedtuple('MockAggregate', ('to_list',))

    async def to_list(*args, **kwargs):
        unique = str(value + 1).zfill(3)
        return [{'registration': unique}]

    return {
        'users': MockUserTable(
            aggregate=lambda *args, **kwargs: MockAggregate(to_list=to_list)
        )
    }


@pytest.fixture
def stub_users_count_0():
    from sop_chatbot import session

    original_db = session.db
    session.db = mock_users_count(0)
    yield
    session.db = original_db


@pytest.fixture
def stub_users_count_10000():
    from sop_chatbot import session

    original_db = session.db
    session.db = mock_users_count(10000)
    yield
    session.db = original_db
