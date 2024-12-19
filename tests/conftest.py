import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from main import app

pytest_plugins = ['tests.fixtures']


@pytest.fixture
def admin_request():
    return {
        'email': 'planetaedevelopment@gmail.com',
        'company_name': 'Planetae Development',
        'company_description': 'A company focused on developing high quality business automations and webapplications.',
        'name': 'Edmilson Monteiro Rodrigues Neto',
        'password': 'This is not my real password',
    }


@pytest.fixture
def async_client():
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://localhost:8000/api',
        timeout=60,
    )


@pytest.fixture
def client():
    return TestClient(app)
