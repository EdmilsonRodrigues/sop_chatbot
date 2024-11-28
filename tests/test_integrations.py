import os
import sys
from httpx import ASGITransport, AsyncClient
import pytest

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from main import app
from models.mixins import CLASS_MAPPING
from models.users import UserRoles


async_client = AsyncClient(
    transport=ASGITransport(app=app), base_url="http://localhost:8000/api", timeout=60
)

name = "Edmilson Monteiro Rodrigues Neto"
password = "This is not my real password"

@pytest.fixture
def admin_request():
    return {
        "email": "planetaedevelopment@gmail.com",
        "company_name": "Planetae Development",
        "company_description": "A company focused on developing high quality business automations and webapplications.",
        "name": name,
        "password": password,
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_signup(admin_request):
    response = await async_client.post("/auth/signup", json=admin_request)
    if response.status_code // 100 != 2:
        assert response.json() == {}
    assert response.status_code == 201
    user = response.json()
    assert user["company"].startswith(CLASS_MAPPING["Company"])
    assert user["company"].endswith("001")
    assert len(user["departments"]) == 1
    assert user["departments"][0].startswith(CLASS_MAPPING["Department"])
    assert user["departments"][0].endswith("001")
    assert user["id"] is not None
    assert user["name"] == admin_request["name"]
    assert user["email"] == admin_request["email"]
    assert user["owner"] == user["registration"]
    assert user["role"] == UserRoles.ADMIN.value
    common = user["owner"].split(".")[1]
    assert (
        common == user["departments"][0].split(".")[1] == user["company"].split(".")[1]
    )
    global admin_registration
    admin_registration = user["registration"]


@pytest.mark.asyncio(loop_scope="session")
async def test_admin_login(admin_request):
    response = await async_client.post(
        "/auth/login", data={"username": admin_registration, "password": admin_request["password"]}
    )
    if response.status_code // 100 != 2:
        assert response.json() == {}
    assert response.status_code == 200
    response = response.json()
    assert response["token_type"] == "bearer"
    assert response["access_token"] is not None
    global admin_headers 
    admin_headers = {"Authorization": f"Bearer {response['access_token']}"}


@pytest.mark.asyncio(loop_scope="session")
async def test_get_me_admin(admin_request):
    response = await async_client.get("/me/", headers=admin_headers)
    if response.status_code // 100 != 2:
        assert response.json() == {}
    assert response.status_code == 200
    user = response.json()
    assert user["company"].startswith(CLASS_MAPPING["Company"])
    assert user["company"].endswith("001")
    assert len(user["departments"]) == 1
    assert user["departments"][0].startswith(CLASS_MAPPING["Department"])
    assert user["departments"][0].endswith("001")
    assert user["id"] is not None
    assert user["name"] == admin_request["name"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_my_company(admin_request):
    response = await async_client.get("me/companies/", headers=admin_headers)
    if response.status_code // 100 != 2:
        assert response.json() == {}
    assert response.status_code == 200
    company = response.json()
    assert company["name"] == admin_request["company_name"]
    assert company["description"] == admin_request["company_description"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_my_departments():
    response = await async_client.get("me/departments/", headers=admin_headers)
    if response.status_code // 100 != 2:
        assert response.json() == {}
    assert response.status_code == 200
    departments = response.json()
    pagination = departments["pagination"]
    assert pagination["page"] == 1
    assert pagination["limit"] == 10
    assert pagination["total"] == 1
    departments = departments["results"]
    assert len(departments) == 1
    assert departments[0]["name"] == "administration"
    assert departments[0]["description"] == "This department is only accessible by the administration"
    assert departments[0]["id"] is not None
    global department_registration
    department_registration = departments[0]["registration"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_my_department():
    response = await async_client.get(f"me/departments/{department_registration}", headers=admin_headers)
    if response.status_code // 100 != 2:
        assert response.json() == {}
    assert response.status_code == 200
    department = response.json()
    assert department["name"] == "administration"
    assert department["description"] == "This department is only accessible by the administration"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_my_name(admin_request):
    response = await async_client.put("me/", headers=admin_headers, json={"name": "Edmilson Rodrigues"})
    if response.status_code // 100 != 2:
        assert response.json() == {}
    assert response.status_code == 200
    user = response.json()
    assert user["name"] == "Edmilson Rodrigues"
    global name
    name = "Edmilson Rodrigues"
    assert user["company"].startswith(CLASS_MAPPING["Company"])
    assert user["company"].endswith("001")
    assert len(user["departments"]) == 1
    assert user["departments"][0].startswith(CLASS_MAPPING["Department"])
    assert user["departments"][0].endswith("001")
    assert user["id"] is not None
    assert user["owner"] == user["registration"]
    assert user["role"] == UserRoles.ADMIN.value
    common = user["owner"].split(".")[1]
    assert (
        common == user["departments"][0].split(".")[1] == user["company"].split(".")[1]
    )


@pytest.mark.asyncio(loop_scope="session")
async def test_update_my_password(admin_request):
    global admin_headers, password
    response = await async_client.put("me/password", headers=admin_headers, json={"old_password": admin_request["password"], "new_password": "This is my real password"})
    if response.status_code // 100 != 2:
        assert response.json() == {}
    assert response.status_code == 200
    user = response.json()
    assert user["name"] == admin_request["name"]
    assert user["company"].startswith(CLASS_MAPPING["Company"])
    assert user["company"].endswith("001")
    assert len(user["departments"]) == 1
    assert user["departments"][0].startswith(CLASS_MAPPING["Department"])
    assert user["departments"][0].endswith("001")
    assert user["id"] is not None
    assert user["owner"] == user["registration"]
    assert user["role"] == UserRoles.ADMIN.value
    common = user["owner"].split(".")[1]
    assert (
        common == user["departments"][0].split(".")[1] == user["company"].split(".")[1]
    )
    password = "This is my real password"
    response = await async_client.post(
        "/auth/login", data={"username": admin_registration, "password": password}
    )
    if response.status_code // 100 != 2:
        assert response.json() == {}
    assert response.status_code == 200
    response = response.json()
    assert response["token_type"] == "bearer"
    assert response["access_token"] is not None
    admin_headers = {"Authorization": f"Bearer {response['access_token']}"}
    

@pytest.mark.asyncio(loop_scope="session")
async def test_admin_get_users(admin_request):
    response = await async_client.get("admin/users/", headers=admin_headers)
    if response.status_code // 100 != 2:
        assert response.json() == {}
    assert response.status_code == 200
    users = response.json()
    pagination = users["pagination"]
    assert pagination["page"] == 1
    assert pagination["limit"] == 10
    assert pagination["total"] == 1
    users = users["results"]
    assert len(users) == 1
    user = users[0]
    assert user["company"].startswith(CLASS_MAPPING["Company"])
    assert user["company"].endswith("001")
    assert len(user["departments"]) == 1
    assert user["departments"][0].startswith(CLASS_MAPPING["Department"])
    assert user["departments"][0].endswith("001")
    assert user["id"] is not None
    assert user["name"] == name
    assert user["owner"] == user["registration"]
    assert user["role"] == UserRoles.ADMIN.value
    common = user["owner"].split(".")[1]
    assert (
        common == user["departments"][0].split(".")[1] == user["company"].split(".")[1]
    )

