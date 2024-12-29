import pytest

from sop_chatbot import session
from sop_chatbot.models.mixins import PaginatedResponse, Pagination


@pytest.mark.asyncio(loop_scope='session')
async def test_get_departments(
    async_client, admin_headers, fill_20_departments
):
    departments = await fill_20_departments
    result = PaginatedResponse(
        pagination=Pagination(total=20), results=departments[:10]
    )
    del departments
    headers = await admin_headers
    response = await async_client.get('/admin/departments/', headers=headers)
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio(loop_scope='session')
async def test_get_no_departments(async_client, admin_headers):
    result = PaginatedResponse(pagination=Pagination(total=0), results=[])
    headers = await admin_headers
    response = await async_client.get('/admin/departments/', headers=headers)
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio(loop_scope='session')
async def test_get_departments_page_2(
    async_client, admin_headers, fill_20_departments
):
    departments = await fill_20_departments
    result = PaginatedResponse(
        pagination=Pagination(total=20, page=2), results=departments[10:]
    )
    del departments
    headers = await admin_headers
    response = await async_client.get(
        '/admin/departments/?skip=1', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio(loop_scope='session')
async def test_get_departments_limit_20(
    async_client, admin_headers, fill_20_departments
):
    departments = await fill_20_departments
    result = PaginatedResponse(
        pagination=Pagination(total=20, limit=20), results=departments
    )
    del departments
    headers = await admin_headers
    response = await async_client.get(
        '/admin/departments/?limit=20', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio(loop_scope='session')
async def test_get_empty_second_page_departments_limit_20(
    async_client, admin_headers, fill_20_departments
):
    departments = await fill_20_departments
    result = PaginatedResponse(
        pagination=Pagination(total=20, page=2, limit=20), results=[]
    )
    del departments
    headers = await admin_headers
    response = await async_client.get(
        '/admin/departments/?skip=1&limit=20', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio
async def test_get_departments_by_name_query(
    async_client, admin_headers, fill_20_departments
):
    departments = await fill_20_departments
    result = PaginatedResponse(
        pagination=Pagination(total=1),
        results=[departments[0]],
    )
    headers = await admin_headers
    response = await async_client.get(
        f'/admin/departments/?query=name&value={departments[0].name}',
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio
async def test_get_departments_by_name_query_no_result(
    async_client, admin_headers, fill_20_departments
):
    departments = await fill_20_departments
    result = PaginatedResponse(pagination=Pagination(total=0), results=[])
    del departments
    headers = await admin_headers
    response = await async_client.get(
        '/admin/departments/?query=name&value=NoName', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio
async def test_create_department(async_client, admin_headers):
    headers = await admin_headers
    response = await async_client.post(
        '/admin/departments/',
        headers=headers,
        json={
            'name': 'Department Name',
            'description': 'Department Description',
        },
    )
    assert response.status_code == 200
    assert response.json()['name'] == 'Department Name'
    assert response.json()['registration'] == '003.0001.001'


@pytest.mark.asyncio
async def test_get_department(async_client, admin_headers, fill_department):
    department = await fill_department
    headers = await admin_headers
    response = await async_client.get(
        f'/admin/departments/{department.registration}', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == department.json()


@pytest.mark.asyncio
async def test_update_department(async_client, admin_headers, fill_department):
    department = await fill_department
    headers = await admin_headers
    new_name = 'New Name'
    response = await async_client.put(
        f'/admin/departments/{department.registration}',
        headers=headers,
        json={'name': new_name, 'description': department.description},
    )
    assert response.status_code == 200
    assert response.json()['name'] == new_name
    assert response.json()['registration'] == department.registration


@pytest.mark.asyncio
async def test_partial_update_department(
    async_client, admin_headers, fill_department
):
    department = await fill_department
    headers = await admin_headers
    new_name = 'New Name'
    response = await async_client.patch(
        f'/admin/departments/{department.registration}',
        headers=headers,
        json={'name': new_name},
    )
    assert response.status_code == 200
    assert response.json()['name'] == new_name
    assert response.json()['registration'] == department.registration


@pytest.mark.asyncio
async def test_delete_department(async_client, admin_headers, fill_department):
    department = await fill_department
    headers = await admin_headers
    response = await async_client.delete(
        f'/admin/departments/{department.registration}', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {
        'action': 'delete',
        'message': 'Department deleted successfully',
    }
    assert (
        await session.db.users.find_one(
            {'departments': [department.registration]}
        )
        is None
    )


@pytest.mark.asyncio
async def test_fail_to_get_departments_from_other_admin(
    async_client, other_admin_headers, fill_20_departments
):
    departments = await fill_20_departments
    result = PaginatedResponse(pagination=Pagination(total=0), results=[])
    del departments
    headers = await other_admin_headers
    response = await async_client.get('/admin/departments/', headers=headers)
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio
async def test_fail_get_department_from_other_admin(
    async_client, other_admin_headers, fill_department
):
    department = await fill_department
    headers = await other_admin_headers
    response = await async_client.get(
        f'/admin/departments/{department.registration}', headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Department does not exist'}


@pytest.mark.asyncio
async def test_fail_update_department_from_other_admin(
    async_client, other_admin_headers, fill_department
):
    department = await fill_department
    headers = await other_admin_headers
    response = await async_client.put(
        f'/admin/departments/{department.registration}',
        headers=headers,
        json={'name': 'New Name', 'description': department.description},
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Department does not exist'}
