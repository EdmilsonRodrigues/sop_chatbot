import pytest

from sop_chatbot import session
from sop_chatbot.models.mixins import PaginatedResponse, Pagination


@pytest.mark.asyncio(loop_scope='session')
async def test_get_users(async_client, admin_headers, fill_20_users):
    users = await fill_20_users
    result = PaginatedResponse(
        pagination=Pagination(total=20), results=users[:10]
    )
    del users
    headers = await admin_headers
    response = await async_client.get('/admin/users/', headers=headers)
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio(loop_scope='session')
async def test_get_no_users(async_client, admin_headers):
    result = PaginatedResponse(pagination=Pagination(total=0), results=[])
    headers = await admin_headers
    response = await async_client.get('/admin/users/', headers=headers)
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio(loop_scope='session')
async def test_get_users_page_2(async_client, admin_headers, fill_20_users):
    users = await fill_20_users
    result = PaginatedResponse(
        pagination=Pagination(total=20, page=2), results=users[10:]
    )
    del users
    headers = await admin_headers
    response = await async_client.get('/admin/users/?skip=1', headers=headers)
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio(loop_scope='session')
async def test_get_users_limit_20(async_client, admin_headers, fill_20_users):
    users = await fill_20_users
    result = PaginatedResponse(
        pagination=Pagination(total=20, limit=20), results=users
    )
    del users
    headers = await admin_headers
    response = await async_client.get(
        '/admin/users/?limit=20', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio(loop_scope='session')
async def test_get_empty_second_page_users_limit_20(
    async_client, admin_headers, fill_20_users
):
    users = await fill_20_users
    result = PaginatedResponse(
        pagination=Pagination(total=20, page=2, limit=20), results=[]
    )
    del users
    headers = await admin_headers
    response = await async_client.get(
        '/admin/users/?skip=1&limit=20', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio
async def test_get_users_by_name_query(
    async_client, admin_headers, fill_20_users
):
    users = await fill_20_users
    result = PaginatedResponse(
        pagination=Pagination(total=1),
        results=[users[0]],
    )
    headers = await admin_headers
    response = await async_client.get(
        f'/admin/users/?query=name&value={users[0].name}',
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio
async def test_get_users_by_name_query_no_result(
    async_client, admin_headers, fill_20_users
):
    users = await fill_20_users
    result = PaginatedResponse(pagination=Pagination(total=0), results=[])
    del users
    headers = await admin_headers
    response = await async_client.get(
        '/admin/users/?query=name&value=NoName', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio
async def test_create_user(async_client, admin_headers):
    headers = await admin_headers
    response = await async_client.post(
        '/admin/users/',
        headers=headers,
        json={
            'name': 'User Name',
            'password': 'password123',
            'company': '002.0001.001',
            'departments': 'Department Name',
        },
    )
    assert response.status_code == 200
    assert response.json()['name'] == 'User Name'
    assert response.json()['registration'] == '003.0001.001'


@pytest.mark.asyncio
async def test_get_user(async_client, admin_headers, fill_user):
    user = await fill_user
    headers = await admin_headers
    response = await async_client.get(
        f'/admin/users/{user.registration}', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == user.json()


@pytest.mark.asyncio
async def test_update_user(async_client, admin_headers, fill_user):
    user = await fill_user
    headers = await admin_headers
    new_name = 'New Name'
    response = await async_client.put(
        f'/admin/users/{user.registration}',
        headers=headers,
        json={
            'name': new_name,
            'password': user.password,
        },
    )
    assert response.status_code == 200
    assert response.json()['name'] == new_name
    assert response.json()['registration'] == user.registration


@pytest.mark.asyncio
async def test_partial_update_user(async_client, admin_headers, fill_user):
    user = await fill_user
    headers = await admin_headers
    new_name = 'New Name'
    response = await async_client.patch(
        f'/admin/users/{user.registration}',
        headers=headers,
        json={'name': new_name},
    )
    assert response.status_code == 200
    assert response.json()['name'] == new_name
    assert response.json()['registration'] == user.registration


@pytest.mark.asyncio
async def test_delete_user(async_client, admin_headers, fill_user):
    user = await fill_user
    headers = await admin_headers
    response = await async_client.delete(
        f'/admin/users/{user.registration}', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {
        'action': 'delete',
        'message': 'User deleted successfully',
    }
    assert (
        await session.db.users.find_one({'registration': user.registration})
        is None
    )


@pytest.mark.asyncio
async def test_fail_to_get_users_from_other_admin(
    async_client, other_admin_headers, fill_20_users
):
    users = await fill_20_users
    result = PaginatedResponse(pagination=Pagination(total=0), results=[])
    del users
    headers = await other_admin_headers
    response = await async_client.get('/admin/users/', headers=headers)
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio
async def test_fail_get_user_from_other_admin(
    async_client, other_admin_headers, fill_user
):
    user = await fill_user
    headers = await other_admin_headers
    response = await async_client.get(
        f'/admin/users/{user.registration}', headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'User does not exist'}


@pytest.mark.asyncio
async def test_fail_update_user_from_other_admin(
    async_client, other_admin_headers, fill_user
):
    user = await fill_user
    headers = await other_admin_headers
    response = await async_client.put(
        f'/admin/users/{user.registration}',
        headers=headers,
        json={
            'name': 'New Name',
            'email': user.email,
            'password': user.password,
        },
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'User does not exist'}
