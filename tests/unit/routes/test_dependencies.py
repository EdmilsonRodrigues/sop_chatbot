import collections
from contextlib import contextmanager
from datetime import datetime, timedelta

import jwt
import pytest
import time_machine
from fastapi import HTTPException

from sop_chatbot import session
from sop_chatbot.config import settings
from sop_chatbot.models.companies import Company
from sop_chatbot.models.departments import Department
from sop_chatbot.models.mixins import (
    ActionResponse,
    PaginatedResponse,
    Pagination,
)
from sop_chatbot.models.users import User
from sop_chatbot.routes.dependencies import (
    AdminListDependency,
    AdminObjectDependency,
    DeleteDependency,
    ListDependency,
    ObjectDependency,
    admin_dependency,
    manager_dependency,
    session_dependency,
)


@pytest.mark.asyncio(loop_scope='session')
async def test_session_dependency(token, stub_find_user_user):
    result = User(
        **{
            'name': 'Edmilson Monteiro Rodrigues Neto',
            'password': 'This is not my real password',
            'role': 'user',
            'company': '002.0001.001',
            'departments': ['003.0001.001'],
            'registration': '001.0001.001',
            'id': '676ef484daff5f784260b96f',
            'created_at': '2024-12-27T18:43:19.339384',
            'updated_at': '2024-12-27T18:43:19.339384',
            'owner': '001.0001.000',
        }
    )

    assert await session_dependency(token) == result


@pytest.mark.asyncio(loop_scope='session')
async def test_session_dependency_fail_invalid_token():
    with pytest.raises(HTTPException) as e:
        await session_dependency('invalid_token')
        assert e.status_code == 401


@pytest.mark.asyncio(loop_scope='session')
async def test_session_dependency_payload_without_sub(time_now):
    with time_machine.travel(time_now, tick=False):
        payload = {
            'exp': datetime.fromisoformat(time_now) + timedelta(days=7),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        with pytest.raises(HTTPException) as e:
            await session_dependency(token)
            assert e.status_code == 401


@pytest.mark.asyncio(loop_scope='session')
async def test_session_dependency_fail_user_not_found(
    token, stub_find_user_none
):
    with pytest.raises(HTTPException) as e:
        await session_dependency(token)
        assert e.status_code == 401


@pytest.mark.asyncio(loop_scope='session')
async def test_admin_dependency(token, stub_find_user_admin):
    result = User(
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
            'departments': ['003.0001.001'],
            'registration': '001.0001.000',
            'company': '002.0001.001',
            'created_at': '2024-12-27T18:43:19.339384',
            'updated_at': '2024-12-27T18:43:19.339384',
            'owner': '001.0001.000',
        }
    )

    assert await admin_dependency(token) == result


@pytest.mark.asyncio(loop_scope='session')
async def test_admin_dependency_fail_lack_privileges(
    token, stub_find_user_user
):
    with pytest.raises(HTTPException) as e:
        await admin_dependency(token)
        assert e.status_code == 403


@pytest.mark.asyncio(loop_scope='session')
async def test_manager_dependency_passes_with_admin(
    token, stub_find_user_admin
):
    result = User(
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
            'departments': ['003.0001.001'],
            'registration': '001.0001.000',
            'company': '002.0001.001',
            'created_at': '2024-12-27T18:43:19.339384',
            'updated_at': '2024-12-27T18:43:19.339384',
            'owner': '001.0001.000',
        }
    )

    assert await manager_dependency(token) == result


@pytest.mark.asyncio(loop_scope='session')
async def test_manager_dependency_fails_with_user(token, stub_find_user_user):
    with pytest.raises(HTTPException) as e:
        await manager_dependency(token)
        assert e.status_code == 403


@pytest.mark.asyncio(loop_scope='session')
async def test_call_list_dependency(
    token, stub_find_user_user, stub_find_all_users
):
    result = PaginatedResponse(
        pagination=Pagination(page=1, limit=10, total=1),
        results=[
            User(
                **{
                    'name': 'Edmilson Monteiro Rodrigues Neto',
                    'password': 'This is not my real password',
                    'role': 'user',
                    'company': '002.0001.001',
                    'departments': ['003.0001.001'],
                    'registration': '001.0001.001',
                    'id': '676ef484daff5f784260b96f',
                    'created_at': '2024-12-27T18:43:19.339384',
                    'updated_at': '2024-12-27T18:43:19.339384',
                    'owner': '001.0001.000',
                }
            )
        ],
    )

    assert (
        await ListDependency(User)(await session_dependency(token)) == result
    )


@pytest.mark.asyncio
async def test_call_admin_list_dependency(
    token, stub_find_user_admin, stub_find_all_users
):
    result = PaginatedResponse(
        pagination=Pagination(page=1, limit=10, total=1),
        results=[
            User(
                **{
                    'name': 'Edmilson Monteiro Rodrigues Neto',
                    'password': 'This is not my real password',
                    'role': 'user',
                    'company': '002.0001.001',
                    'departments': ['003.0001.001'],
                    'registration': '001.0001.001',
                    'id': '676ef484daff5f784260b96f',
                    'created_at': '2024-12-27T18:43:19.339384',
                    'updated_at': '2024-12-27T18:43:19.339384',
                    'owner': '001.0001.000',
                }
            )
        ],
    )

    assert (
        await AdminListDependency(User)(await admin_dependency(token))
        == result
    )


@pytest.mark.asyncio(loop_scope='session')
async def test_call_object_dependency(token, stub_find_user_user):
    result = User(
        **{
            'name': 'Edmilson Monteiro Rodrigues Neto',
            'password': 'This is not my real password',
            'role': 'user',
            'company': '002.0001.001',
            'departments': ['003.0001.001'],
            'registration': '001.0001.001',
            'id': '676ef484daff5f784260b96f',
            'created_at': '2024-12-27T18:43:19.339384',
            'updated_at': '2024-12-27T18:43:19.339384',
            'owner': '001.0001.000',
        }
    )

    assert (
        await ObjectDependency(User, foreign_key='registration')(
            await session_dependency(token), '001.0001.001'
        )
        == result
    )


@pytest.mark.asyncio
async def test_fail_call_object_dependency_object_not_found(
    token, stub_find_user_user, stub_company_find_none
):
    with pytest.raises(HTTPException) as e:
        await ObjectDependency(Company, foreign_key='registration')(
            await session_dependency(token), '001.0001.001'
        )
        assert e.status_code == 404


@pytest.mark.asyncio
async def test_fail_call_object_dependency_unauthorized(
    token, stub_find_user_user, stub_company_find
):
    with pytest.raises(HTTPException) as e:
        await ObjectDependency(Company, foreign_key='user')(
            await session_dependency(token), '002.0001.001'
        )
        assert e.status_code == 403


@pytest.mark.asyncio
async def test_call_object_dependency_find_company(
    token, stub_find_user_user, stub_company_find
):
    result = Company(
        **{
            'name': 'Planetae Development',
            'description': 'A company focused on developing',
            'registration': '002.0001.001',
            'owner': '001.0001.000',
            'created_at': '2024-12-27T18:43:19.339384',
            'updated_at': '2024-12-27T18:43:19.339384',
            'id': '676ef484daff5f784260b96f',
        }
    )

    assert (
        await ObjectDependency(Company, foreign_key='company')(
            await session_dependency(token), '002.0001.001'
        )
        == result
    )


@pytest.mark.asyncio
async def test_call_object_dependency_find_department(
    token, stub_find_user_user, stub_department_find
):
    result = Department(
        **{
            'name': 'Development Department',
            'description': 'A department focused on development',
            'registration': '003.0001.001',
            'owner': '001.0001.000',
            'created_at': '2024-12-27T18:43:19.339384',
            'updated_at': '2024-12-27T18:43:19.339384',
            'id': '676ef484daff5f784260b96f',
            'company': '002.0001.001',
        }
    )

    assert (
        await ObjectDependency(Department, relational_list='departments')(
            await session_dependency(token), '003.0001.001'
        )
        == result
    )


@pytest.mark.asyncio
async def test_call_admin_object_dependency(token, stub_find_user_admin):
    result = User(
        **{
            'name': 'Edmilson Monteiro Rodrigues Neto',
            'password': 'This is not my real password',
            'role': 'admin',
            'company': '002.0001.001',
            'departments': ['003.0001.001'],
            'registration': '001.0001.000',
            'id': '676ef484daff5f784260b96e',
            'created_at': '2024-12-27T18:43:19.339384',
            'updated_at': '2024-12-27T18:43:19.339384',
            'owner': '001.0001.000',
        }
    )

    assert (
        await AdminObjectDependency(User, foreign_key='registration')(
            await admin_dependency(token), '001.0001.001'
        )
        == result
    )


@pytest.mark.asyncio
async def test_fail_call_admin_object_dependency_object_not_found(
    token, stub_find_user_admin, stub_company_find_none
):
    with pytest.raises(HTTPException) as e:
        await AdminObjectDependency(Company, foreign_key='registration')(
            await admin_dependency(token), '001.0001.001'
        )
        assert e.status_code == 404


@pytest.mark.asyncio
async def test_fail_call_admin_object_dependency_unauthorized(
    token, stub_find_user_admin, stub_company_find, admin
):
    @contextmanager
    def monkey_patch_admin_registration():
        admin['registration'] = '001.0002.000'

        def mock_find_user():
            MockUserTable = collections.namedtuple(
                'MockUserTable', ('find_one',)
            )

            async def find_one(*args, **kwargs):
                if args[0].get('owner') == admin['registration']:
                    return admin

            return MockUserTable(find_one=find_one)

        original = session.db
        session.db['users'] = mock_find_user()
        yield
        session.db = original

    with pytest.raises(HTTPException) as e:
        with monkey_patch_admin_registration():
            await AdminObjectDependency(Company)(
                await admin_dependency(token), '002.0001.001'
            )
            assert e.status_code == 404


@pytest.mark.asyncio
async def test_call_delete_dependency(
    token, stub_find_user_user, stub_department_find
):
    result = ActionResponse(
        **{'action': 'delete', 'message': 'Department deleted successfully'}
    )
    object_dependency = ObjectDependency(
        Department, relational_list='departments'
    )
    delete_dependency = DeleteDependency(object_dependency=object_dependency)

    assert delete_dependency._get_object_dependency() == object_dependency

    assert (
        await delete_dependency(
            await object_dependency(
                await session_dependency(token), '003.0001.001'
            )
        )
    ) == result
