from datetime import datetime, timedelta

import pytest
import time_machine


@pytest.mark.asyncio(loop_scope='session')
async def test_login(async_client, fill_user):
    user = await fill_user
    response = await async_client.post(
        '/auth/login',
        data={'username': user.registration, 'password': user.password},
    )
    assert response.status_code == 200

    assert response.json()['access_token']
    assert response.json()['token_type'] == 'bearer'


@pytest.mark.asyncio(loop_scope='session')
async def test_login_invalid_credentials(async_client, fill_user):
    user = await fill_user
    response = await async_client.post(
        '/auth/login',
        data={'username': user.registration, 'password': 'invalid'},
    )
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope='session')
async def test_login_invalid_registration(async_client, fill_user):
    user = await fill_user
    response = await async_client.post(
        '/auth/login', data={'username': 'invalid', 'password': user.password}
    )
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope='session')
async def test_signup(async_client):
    response = await async_client.post(
        '/auth/signup',
        json={
            'name': 'test',
            'email': 'test@test.com',
            'password': 'test',
            'company_name': 'test',
            'company_description': 'test',
        },
    )

    assert response.status_code == 201
    assert response.json()['registration']
    assert response.json()['name'] == 'test'
    assert response.json()['email'] == 'test@test.com'
    assert response.json()['role'] == 'admin'


@pytest.mark.asyncio(loop_scope='session')
async def test_admin_login(async_client, fill_admin):
    admin = await fill_admin
    response = await async_client.post(
        '/auth/admin/login',
        data={'username': admin.email, 'password': admin.password},
    )
    assert response.status_code == 200

    assert response.json()['access_token']
    assert response.json()['token_type'] == 'bearer'


@pytest.mark.asyncio(loop_scope='session')
async def test_admin_login_invalid_credentials(async_client, fill_admin):
    admin = await fill_admin
    response = await async_client.post(
        '/auth/admin/login',
        data={'username': admin.email, 'password': 'invalid'},
    )
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope='session')
async def test_admin_login_invalid_email(async_client, fill_admin):
    admin = await fill_admin
    response = await async_client.post(
        '/auth/admin/login',
        data={'username': 'invalid', 'password': admin.password},
    )
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope='session')
async def test_refresh(async_client, user_access_token):
    access_token = await user_access_token
    response = await async_client.post(
        '/auth/refresh',
        headers={'Authorization': f'Bearer {access_token}'},
    )

    assert response.status_code == 200
    assert response.json()['access_token']
    assert response.json()['token_type'] == 'bearer'


@pytest.mark.asyncio(loop_scope='session')
async def test_refresh_expired_token(async_client, user_access_token):
    expired_token = await user_access_token

    with time_machine.travel(datetime.now() + timedelta(days=8)):
        response = await async_client.post(
            '/auth/refresh',
            headers={'Authorization': f'Bearer {expired_token}'},
        )
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid token'
