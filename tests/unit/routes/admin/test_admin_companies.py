import pytest

from sop_chatbot.models.mixins import PaginatedResponse, Pagination


@pytest.mark.asyncio(loop_scope='session')
async def test_get_companies(async_client, admin_headers, fill_20_companies):
    companies = await fill_20_companies
    result = PaginatedResponse(
        pagination=Pagination(total=20), results=companies[:10]
    )
    del companies
    headers = await admin_headers
    response = await async_client.get('/admin/companies/', headers=headers)
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio(loop_scope='session')
async def test_get_no_companies(async_client, admin_headers):
    result = PaginatedResponse(pagination=Pagination(total=0), results=[])
    headers = await admin_headers
    response = await async_client.get('/admin/companies/', headers=headers)
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio(loop_scope='session')
async def test_get_companies_page_2(
    async_client, admin_headers, fill_20_companies
):
    companies = await fill_20_companies
    result = PaginatedResponse(
        pagination=Pagination(total=20, page=2), results=companies[10:]
    )
    del companies
    headers = await admin_headers
    response = await async_client.get(
        '/admin/companies/?skip=1', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio(loop_scope='session')
async def test_get_companies_limit_20(
    async_client, admin_headers, fill_20_companies
):
    companies = await fill_20_companies
    result = PaginatedResponse(
        pagination=Pagination(total=20, limit=20), results=companies
    )
    del companies
    headers = await admin_headers
    response = await async_client.get(
        '/admin/companies/?limit=20', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio(loop_scope='session')
async def test_get_empty_second_page_companies_limit_20(
    async_client, admin_headers, fill_20_companies
):
    companies = await fill_20_companies
    result = PaginatedResponse(
        pagination=Pagination(total=20, page=2, limit=20), results=[]
    )
    del companies
    headers = await admin_headers
    response = await async_client.get(
        '/admin/companies/?skip=1&limit=20', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio
async def test_get_companies_by_name_query(
    async_client, admin_headers, fill_20_companies
):
    companies = await fill_20_companies
    result = PaginatedResponse(
        pagination=Pagination(total=1),
        results=[companies[0]],
    )
    headers = await admin_headers
    response = await async_client.get(
        f'/admin/companies/?query=name&value={companies[0].name}',
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio
async def test_get_companies_by_name_query_no_result(
    async_client, admin_headers, fill_20_companies
):
    companies = await fill_20_companies
    result = PaginatedResponse(pagination=Pagination(total=0), results=[])
    del companies
    headers = await admin_headers
    response = await async_client.get(
        '/admin/companies/?query=name&value=NoName', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio
async def test_get_company(async_client, admin_headers, fill_company):
    company = await fill_company
    headers = await admin_headers
    response = await async_client.get(
        f'/admin/companies/{company.registration}', headers=headers
    )
    assert response.status_code == 200
    assert response.json() == company.json()


@pytest.mark.asyncio
async def test_update_company(async_client, admin_headers, fill_company):
    company = await fill_company
    headers = await admin_headers
    new_name = 'New Name'
    response = await async_client.put(
        f'/admin/companies/{company.registration}',
        headers=headers,
        json={'name': new_name, 'description': company.description},
    )
    assert response.status_code == 200
    assert response.json()['name'] == new_name
    assert response.json()['registration'] == company.registration


@pytest.mark.asyncio
async def test_partial_update_company(
    async_client, admin_headers, fill_company
):
    company = await fill_company
    headers = await admin_headers
    new_name = 'New Name'
    response = await async_client.patch(
        f'/admin/companies/{company.registration}',
        headers=headers,
        json={'name': new_name},
    )
    assert response.status_code == 200
    assert response.json()['name'] == new_name
    assert response.json()['registration'] == company.registration


@pytest.mark.asyncio
async def test_fail_to_get_companies_from_other_admin(
    async_client, other_admin_headers, fill_20_companies
):
    companies = await fill_20_companies
    result = PaginatedResponse(pagination=Pagination(total=0), results=[])
    del companies
    headers = await other_admin_headers
    response = await async_client.get('/admin/companies/', headers=headers)
    assert response.status_code == 200
    assert response.json() == result.json()


@pytest.mark.asyncio
async def test_fail_get_company_from_other_admin(
    async_client, other_admin_headers, fill_company
):
    company = await fill_company
    headers = await other_admin_headers
    response = await async_client.get(
        f'/admin/companies/{company.registration}', headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Company does not exist'}


@pytest.mark.asyncio
async def test_fail_update_company_from_other_admin(
    async_client, other_admin_headers, fill_company
):
    company = await fill_company
    headers = await other_admin_headers
    response = await async_client.put(
        f'/admin/companies/{company.registration}',
        headers=headers,
        json={'name': 'New Name', 'description': company.description},
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Company does not exist'}
