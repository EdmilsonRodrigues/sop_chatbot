import pytest
import time_machine

from sop_chatbot.models.departments import CreateDepartmentRequest, Department


def test_department_table_name():
    assert Department.table_name() == 'departments'


@pytest.mark.asyncio(loop_scope='session')
async def test_department_gen_registration_0(stub_departments_count_0):
    assert await Department.gen_registration('001.0001.000') == '003.0001.001'


@pytest.mark.asyncio(loop_scope='session')
async def test_department_gen_registration_10000(stub_departments_count_10000):
    assert (
        await Department.gen_registration('001.10001.000') == '003.10001.10001'
    )


@pytest.mark.asyncio(loop_scope='session')
async def test_create_department(department_request, stub_department_creation):
    result = Department(
        **{
            'id': '676ef484daff5f784260b96f',
            'name': 'Development Department',
            'description': 'A department focused on development',
            'registration': '003.0001.001',
            'owner': '001.0001.000',
            'created_at': '2024-12-27T18:43:19.339384',
            'updated_at': '2024-12-27T18:43:19.339384',
            'company': '002.0001.001',
        }
    )

    with time_machine.travel('2024-12-27 18:43:19.339384', tick=False):
        department = await Department.create(
            CreateDepartmentRequest(**department_request),
            '001.0001.000',
            '002.0001.001',
        )

    assert department == result
