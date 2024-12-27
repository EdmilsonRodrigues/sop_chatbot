from datetime import datetime

import pytest

from sop_chatbot.models.users import Admin, User


def test_admin_table_name():
    assert Admin.table_name() == 'users'


def test_user_table_name():
    assert User.table_name() == 'users'


@pytest.mark.asyncio(loop_scope='session')
async def test_get_admin_none(stub_find_user_none):
    assert await Admin.get('001.0001.000') is None


@pytest.mark.asyncio(loop_scope='session')
async def test_get_user_none(stub_find_user_none):
    assert await User.get('001.0001.000') is None


@pytest.mark.asyncio(loop_scope='session')
async def test_get_admin_user(stub_find_user_admin, admin):
    result = Admin(
        **{
            'id': '676ef484daff5f784260b96e',
            'email': 'planetaedevelopment@gmail.com',
            'company_name': 'Planetae Development',
            'company_description': ' '.join(
                (
                    'A company focused on developing',
                    'high quality business automations and webapplications.',
                )
            ),
            'name': 'Edmilson Monteiro Rodrigues Neto',
            'password': 'This is not my real password',
            'role': 'admin',
            'departments': ['003.0001.000'],
            'registration': '001.0001.000',
            'company': '002.0001.000',
            'created_at': '2024-12-27T18:43:19.339384',
            'updated_at': '2024-12-27T18:43:19.339384',
            'owner': '001.0001.000',
        }
    )
    assert await Admin.get('001.0001.000') == result


@pytest.mark.asyncio(loop_scope='session')
async def test_get_user_user(stub_find_user_user, user):
    result = User(
        **{
            'name': 'Edmilson Monteiro Rodrigues Neto',
            'password': 'This is not my real password',
            'role': 'user',
            'company': '002.0001.000',
            'departments': ['003.0001.000'],
            'registration': '001.0001.001',
            'id': '676ef484daff5f784260b96f',
            'created_at': '2024-12-27T18:43:19.339384',
            'updated_at': '2024-12-27T18:43:19.339384',
            'owner': '001.0001.000',
        }
    )
    assert await User.get('001.0001.000') == result


def test_admin_json(admin_object):
    result = {
        'id': '676ef484daff5f784260b96e',
        'email': 'planetaedevelopment@gmail.com',
        'company_name': 'Planetae Development',
        'company_description': ' '.join(
            (
                'A company focused on developing',
                'high quality business automations and webapplications.',
            )
        ),
        'name': 'Edmilson Monteiro Rodrigues Neto',
        'role': 'admin',
        'departments': ['003.0001.000'],
        'registration': '001.0001.000',
        'company': '002.0001.000',
        'created_at': '2024-12-27T18:43:19.339384',
        'updated_at': '2024-12-27T18:43:19.339384',
        'owner': '001.0001.000',
    }
    assert admin_object.json() == result


def test_user_json(user_object):
    result = {
        'name': 'Edmilson Monteiro Rodrigues Neto',
        'role': 'user',
        'company': '002.0001.000',
        'departments': ['003.0001.000'],
        'registration': '001.0001.001',
        'id': '676ef484daff5f784260b96f',
        'created_at': '2024-12-27T18:43:19.339384',
        'updated_at': '2024-12-27T18:43:19.339384',
        'owner': '001.0001.000',
    }
    assert user_object.json() == result


def test_user_mongo(user_object):
    result = {
        'name': 'Edmilson Monteiro Rodrigues Neto',
        'role': 'user',
        'company': '002.0001.000',
        'departments': ['003.0001.000'],
        'registration': '001.0001.001',
        'created_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
        'updated_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
        'owner': '001.0001.000',
    }
    assert user_object.mongo() == result


def test_admin_mongo(admin_object):
    result = {
        'email': 'planetaedevelopment@gmail.com',
        'company_name': 'Planetae Development',
        'company_description': ' '.join(
            (
                'A company focused on developing',
                'high quality business automations and webapplications.',
            )
        ),
        'name': 'Edmilson Monteiro Rodrigues Neto',
        'role': 'admin',
        'departments': ['003.0001.000'],
        'registration': '001.0001.000',
        'company': '002.0001.000',
        'created_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
        'updated_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
        'owner': '001.0001.000',
    }
    assert admin_object.mongo() == result


def test_verify_password(user_object):
    user_object.password = (
        'afe1fa4af3b95b86bf07c6d70c86cd54d5b20a670fb59645720e42f18a635525'
    )
    assert user_object.verify_password('This is not my real password')


def test_admin_is_admin(admin_object):
    assert admin_object.is_admin


def test_user_is_not_admin(user_object):
    assert not user_object.is_admin


def test_admin_is_manager(admin_object):
    assert admin_object.is_manager


def test_user_is_not_manager(user_object):
    assert not user_object.is_manager


@pytest.mark.asyncio(loop_scope='session')
async def test_gen_admin_registration(stub_users_count_0):
    result = ('001.0001.000', '001.0001.000')

    assert await Admin.gen_registration('001.0001.000') == result


@pytest.mark.asyncio(loop_scope='session')
async def test_gen_user_registration(stub_users_count_0):
    result = ('001.0001.001', '001.0001.000')

    assert await User.gen_registration() == (result, result)


@pytest.mark.asyncio(loop_scope='session')
async def test_gen_admin_registration_10000(stub_users_count_10000):
    result = '001.10001.000'

    assert await Admin.gen_registration() == (result, result)


@pytest.mark.asyncio(loop_scope='session')
async def test_gen_user_registration_10000(stub_users_count_10000):
    result = '001.10001.001'

    assert await User.gen_registration() == (result, result)
