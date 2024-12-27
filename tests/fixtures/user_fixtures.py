import pytest


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


def mock_find_user(value: dict | None = None):
    class MockUserTable:
        async def find_one(self, *args, **kwargs):
            return value

    return {'users': MockUserTable()}


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


def mock_users_count(value: int = 0):
    class MockUserTable:
        async def count_documents(self, *args, **kwargs):
            return value

    return {'users': MockUserTable()}


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
