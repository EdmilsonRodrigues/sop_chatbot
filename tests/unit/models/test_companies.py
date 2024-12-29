import pytest
import time_machine

from sop_chatbot.models.companies import Company, CreateCompanyRequest


def test_company_table_name():
    assert Company.table_name() == 'companies'


@pytest.mark.asyncio(loop_scope='session')
async def test_company_gen_registration_0(stub_companies_count_0):
    assert await Company.gen_registration('001.0001.000') == '002.0001.001'


@pytest.mark.asyncio(loop_scope='session')
async def test_company_gen_registration_10000(stub_companies_count_10000):
    assert await Company.gen_registration('001.10001.000') == '002.10001.10001'


@pytest.mark.asyncio(loop_scope='session')
async def test_create_company(company_request, stub_company_creation):
    result = Company(
        **{
            'id': '676ef484daff5f784260b96f',
            'name': 'Planetae Development',
            'description': 'A company focused on developing',
            'registration': '002.0001.001',
            'owner': '001.0001.000',
            'created_at': '2024-12-27T18:43:19.339384',
            'updated_at': '2024-12-27T18:43:19.339384',
        }
    )

    with time_machine.travel('2024-12-27 18:43:19.339384', tick=False):
        company = await Company.create(
            CreateCompanyRequest(**company_request), '001.0001.000'
        )

    assert company == result
