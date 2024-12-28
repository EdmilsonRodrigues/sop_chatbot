from datetime import datetime

import pytest
import time_machine

from sop_chatbot.models.mixins import (
    ActionResponse,
    PaginatedResponse,
    Pagination,
    PaginationRequest,
)


def test_mock_table_name(MockClass):
    assert MockClass.table_name() == 'mocks'


def test_mock_object_to_mongo(mock_object):
    result = {
        'registration': '000.0000.000',
        'created_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
        'updated_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
        'owner': '001.0000.000',
        'company': '002.0000.000',
    }
    assert mock_object.mongo() == result


def test_complex_mock_object_to_mongo(complex_mock_object):
    result = {
        'registration': '000.0000.000',
        'created_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
        'updated_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
        'owner': '001.0000.000',
        'company': '002.0000.000',
        'workspace_id': '676ff4ea01892d16d07c41b4',
        'composed_class': {
            'id': '676ff4ea01892d16d07c41b4',
            'registration': '000.0000.000',
            'created_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
            'updated_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
            'owner': '001.0000.000',
            'company': '002.0000.000',
        },
        'composed_enum': 'mock',
        'composed_array': [1, 2, 3],
    }
    assert complex_mock_object.mongo() == result


def test_mock_object_to_json(mock_object):
    result = {
        'id': '676ff4ea01892d16d07c41b4',
        'registration': '000.0000.000',
        'created_at': '2024-12-27T18:43:19.339384',
        'updated_at': '2024-12-27T18:43:19.339384',
        'owner': '001.0000.000',
        'company': '002.0000.000',
    }
    assert mock_object.json() == result


def test_complex_mock_object_to_json(complex_mock_object):
    result = {
        'id': '676ff4ea01892d16d07c41b4',
        'registration': '000.0000.000',
        'created_at': '2024-12-27T18:43:19.339384',
        'updated_at': '2024-12-27T18:43:19.339384',
        'owner': '001.0000.000',
        'company': '002.0000.000',
        'workspace_id': '676ff4ea01892d16d07c41b4',
        'composed_class': {
            'id': '676ff4ea01892d16d07c41b4',
            'registration': '000.0000.000',
            'created_at': '2024-12-27T18:43:19.339384',
            'updated_at': '2024-12-27T18:43:19.339384',
            'owner': '001.0000.000',
            'company': '002.0000.000',
        },
        'composed_enum': 'mock',
        'composed_array': [1, 2, 3],
    }
    assert complex_mock_object.json() == result


@pytest.mark.asyncio
async def test_update_mock_object(mock_object, stub_update_mock_object):
    data = {
        'owner': '002.0000.000',
        'company': '003.0000.000',
    }
    result = {
        'id': '676ff4ea01892d16d07c41b4',
        'registration': '000.0000.000',
        'created_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
        'updated_at': datetime(2024, 12, 27, 18, 45, 10, 0),
        'owner': '002.0000.000',
        'company': '003.0000.000',
    }

    with time_machine.travel(datetime(2024, 12, 27, 18, 45, 10), tick=False):
        updated = await mock_object.update(data)

    assert updated.model_dump() == result


@pytest.mark.asyncio
async def test_create_mock_object(
    mock_object, MockRequest, stub_create_mock_object
):
    result = {
        'id': '676ff4ea01892d16d07c41b4',
        'registration': '000.0000.000',
        'created_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
        'updated_at': datetime(2024, 12, 27, 18, 43, 19, 339384),
        'owner': '001.0000.000',
        'company': '002.0000.000',
    }

    request = MockRequest(company='002.0000.000')

    with time_machine.travel(
        datetime(2024, 12, 27, 18, 43, 19, 339384), tick=False
    ):
        created = await mock_object.create(request, '001.0000.000')

    assert created.model_dump() == result


@pytest.mark.asyncio
async def test_gen_mock_registration(stub_mocks_count_0, MockClass):
    assert await MockClass.gen_registration('001.0000.000') == '000.0000.001'


@pytest.mark.asyncio
async def test_get_mock(MockClass, stub_find_one_mock_object):
    result = MockClass(
        id='676ff4ea01892d16d07c41b4',
        registration='000.0000.000',
        created_at=datetime(2024, 12, 27, 18, 43, 19, 339384),
        updated_at=datetime(2024, 12, 27, 18, 43, 19, 339384),
        owner='001.0000.000',
        company='002.0000.000',
    )
    assert await MockClass.get('000.0000.000') == result


@pytest.mark.asyncio
async def test_get_mock_by_field(MockClass, stub_find_one_mock_object):
    result = MockClass(
        id='676ff4ea01892d16d07c41b4',
        registration='000.0000.000',
        created_at=datetime(2024, 12, 27, 18, 43, 19, 339384),
        updated_at=datetime(2024, 12, 27, 18, 43, 19, 339384),
        owner='001.0000.000',
        company='002.0000.000',
    )
    assert (
        await MockClass.get_by_field('id', '676ff4ea01892d16d07c41b4')
        == result
    )


@pytest.mark.asyncio
async def test_get_all_mocks_when_user_registration_does_not_exist(
    MockClass, stub_find_user_none
):
    result = PaginatedResponse(pagination=Pagination(), results=[])

    assert (
        await MockClass.get_all(
            PaginationRequest(), '001.0000.000', '001.0000.001'
        )
        == result
    )


@pytest.mark.asyncio
async def test_get_all_mocks_when_user_registration_exists_using_queries(
    MockClass, stub_find_all_mocks
):
    result = PaginatedResponse(
        pagination=Pagination(total=1),
        results=[
            MockClass(
                **{
                    'id': '676ff4ea01892d16d07c41b4',
                    'registration': '000.0000.000',
                    'created_at': '2024-12-27T18:43:19.339384',
                    'updated_at': '2024-12-27T18:43:19.339384',
                    'owner': '001.0000.000',
                    'company': '002.0000.000',
                }
            )
        ],
    )

    assert (
        await MockClass.get_all(
            PaginationRequest(query='mock'), '001.0000.000', '001.0000.000'
        )
        == result
    )


@pytest.mark.asyncio
async def test_delete_mock_object(mock_object, stub_delete_mock_object):
    result = ActionResponse(
        **{
            'action': 'delete',
            'message': 'Mock deleted successfully',
        }
    )
    assert await mock_object.delete() == result


def test_paginated_response_to_json():
    result = {
        'pagination': {
            'page': 1,
            'limit': 10,
            'total': 100,
        },
        'results': [],
    }
    assert (
        PaginatedResponse(
            pagination=Pagination(page=1, limit=10, total=100), results=[]
        ).json()
        == result
    )
