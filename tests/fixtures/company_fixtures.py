import collections

import pytest

from tests.conftest import MockInsertOne


def mock_company_count(value: int = 0):
    MockCompanyTable = collections.namedtuple(
        'MockCompanyTable', ('count_documents',)
    )

    async def count_documents(*args, **kwargs):
        return value

    return {'companies': MockCompanyTable(count_documents=count_documents)}


@pytest.fixture
def stub_companies_count_0():
    from sop_chatbot import session

    original_db = session.db
    session.db = mock_company_count(0)
    yield
    session.db = original_db


@pytest.fixture
def stub_companies_count_10000():
    from sop_chatbot import session

    original_db = session.db
    session.db = mock_company_count(10000)
    yield
    session.db = original_db


@pytest.fixture
def company_request():
    return {
        'name': 'Planetae Development',
        'description': 'A company focused on developing',
    }


@pytest.fixture
def company(time_now):
    return {
        '_id': '676ef484daff5f784260b96f',
        'name': 'Planetae Development',
        'description': 'A company focused on developing',
        'registration': '002.0001.001',
        'owner': '001.0001.000',
        'created_at': time_now,
        'updated_at': time_now,
    }


@pytest.fixture
def company_object(company):
    from sop_chatbot.models.companies import Company

    return Company(**company, id=company['_id'])


def mock_company_creation(id: str):
    from bson import ObjectId

    async def insert_one(*args, **kwargs):
        return MockInsertOne(ObjectId(id))

    return insert_one


@pytest.fixture
def stub_company_creation(stub_companies_count_0):
    from sop_chatbot import session

    MockCompanyTable = collections.namedtuple(
        'MockCompanyTable', ('insert_one', 'count_documents')
    )
    original_db = session.db
    session.db['companies'] = MockCompanyTable(
        insert_one=mock_company_creation('676ef484daff5f784260b96f'),
        count_documents=session.db['companies'].count_documents,
    )
    yield
    session.db = original_db
