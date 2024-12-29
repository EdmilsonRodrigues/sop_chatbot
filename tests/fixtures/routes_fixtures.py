import factory
import faker
import pytest
from bson import ObjectId

from sop_chatbot import session
from sop_chatbot.models.companies import Company
from sop_chatbot.models.departments import Department
from sop_chatbot.models.users import Admin, User
from sop_chatbot.services.auth import Auth

fake = faker.Faker()


class UserFactory(factory.Factory):
    class Meta:
        model = User

    name = factory.Sequence(lambda n: f'test{n}')
    password = 'password'
    role = 'user'
    company = '002.0001.001'
    departments = ['003.0001.001']
    id = factory.Sequence(lambda n: str(ObjectId()))
    registration = factory.Sequence(
        lambda n: f'001.0001.{str(n + 1).zfill(3)}'
    )
    created_at = '2024-12-27T18:43:19'
    updated_at = '2024-12-27T18:43:19'
    owner = '001.0001.000'


class AdminFactory(factory.Factory):
    class Meta:
        model = Admin

    name = factory.Sequence(lambda n: f'test{n}')
    password = 'password'
    role = 'admin'
    company = factory.LazyAttribute(
        lambda admin: f'002.{admin.registration.split('.')[1]}.001'
    )
    departments = factory.LazyAttribute(
        lambda admin: [f'003.{admin.registration.split('.')[1]}.001']
    )
    id = factory.Sequence(lambda n: str(ObjectId()))
    registration = factory.Sequence(lambda n: f'001.{str(n + 1).zfill(4)}.000')
    email = factory.LazyAttribute(lambda admin: f'{admin.name}@test.com')
    created_at = '2024-12-27T18:43:19'
    updated_at = '2024-12-27T18:43:19'
    owner = factory.LazyAttribute(lambda admin: admin.registration)
    company_name = 'test'
    company_description = 'test'


class CompanyFactory(factory.Factory):
    class Meta:
        model = Company

    id = factory.Sequence(lambda n: str(ObjectId()))
    name = factory.Sequence(lambda n: f'test{n}')
    description = fake.text()
    registration = factory.Sequence(
        lambda n: f'002.0001.{str(n + 1).zfill(3)}'
    )
    created_at = '2024-12-27T18:43:19'
    updated_at = '2024-12-27T18:43:19'
    owner = '001.0001.000'


class DepartmentFactory(factory.Factory):
    class Meta:
        model = Department

    id = str(ObjectId())
    name = factory.Sequence(lambda n: f'test{n}')
    description = fake.text()
    registration = factory.Sequence(
        lambda n: f'003.0001.{str(n + 1).zfill(3)}'
    )
    company = '002.0001.001'
    created_at = '2024-12-27T18:43:19'
    updated_at = '2024-12-27T18:43:19'
    owner = '001.0001.000'


@pytest.fixture
def fill_20_users():
    users = UserFactory.create_batch(20)
    db_users = []
    for user in users:
        user = user.model_dump()
        user['_id'] = ObjectId(user.pop('id'))
        user['password'] = Auth.encrypt_password(user['password'])
        db_users.append(user)
    session.db.users.insert_many(db_users)
    return users


@pytest.fixture
async def fill_user():
    user = UserFactory()
    db_user = user.model_dump()
    db_user['_id'] = ObjectId(db_user.pop('id'))
    db_user['password'] = Auth.encrypt_password(db_user['password'])
    await session.db.users.insert_one(db_user)
    return user


@pytest.fixture
async def fill_admin():
    user = AdminFactory(registration='001.0001.000')
    db_user = user.model_dump()
    db_user['_id'] = ObjectId(db_user.pop('id'))
    db_user['password'] = Auth.encrypt_password(db_user['password'])
    await session.db.users.insert_one(db_user)
    return user


@pytest.fixture
async def user_access_token(fill_user):
    user = await fill_user
    return Auth.generate_jwt(user.registration)


@pytest.fixture
async def user_headers(user_access_token):
    return {'Authorization': f'Bearer {await user_access_token}'}


@pytest.fixture
async def admin_access_token(fill_admin):
    admin = await fill_admin
    return Auth.generate_jwt(admin.registration)


@pytest.fixture
async def admin_headers(admin_access_token):
    return {'Authorization': f'Bearer {await admin_access_token}'}


@pytest.fixture
async def other_admin_headers():
    admin = AdminFactory(registration='001.0002.000')
    db_admin = admin.model_dump()
    db_admin['_id'] = ObjectId(db_admin.pop('id'))
    db_admin['password'] = Auth.encrypt_password(db_admin['password'])
    await session.db.users.insert_one(db_admin)
    return {'Authorization': f'Bearer {Auth.generate_jwt(admin.registration)}'}


@pytest.fixture
async def fill_company():
    company = CompanyFactory()
    db_company = company.model_dump()
    db_company['_id'] = ObjectId(db_company.pop('id'))
    await session.db.companies.insert_one(db_company)
    return company


@pytest.fixture
async def fill_20_companies():
    companies = CompanyFactory.create_batch(20)
    db_companies = []
    for company in companies:
        company = company.model_dump()
        company['_id'] = ObjectId(company.pop('id'))
        db_companies.append(company)
    await session.db.companies.insert_many(db_companies)
    return companies
