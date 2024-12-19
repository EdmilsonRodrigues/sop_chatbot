from datetime import datetime
from typing import Annotated

from pydantic import Field

from models.mixins import BaseClass, BaseRequest
from session import db


class CreateCompanyRequest(BaseRequest):
    name: Annotated[str, Field(description='The name of the company')]
    description: Annotated[
        str, Field(description='The description of the company')
    ]


class Company(BaseClass, CreateCompanyRequest):
    @classmethod
    def table_name(cls):
        return 'companies'

    @classmethod
    async def create(cls, create_request: BaseRequest, owner: str, **kwargrs):
        created_at = datetime.now()
        updated_at = datetime.now()
        registration = await cls.gen_registration(owner)
        id = (
            await db[cls.table_name()].insert_one(
                {
                    **create_request.mongo(),
                    'registration': registration,
                    'owner': owner,
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'company': registration,
                    **kwargrs,
                }
            )
        ).inserted_id
        self = cls(
            id=str(id),
            created_at=created_at,
            updated_at=updated_at,
            registration=registration,
            owner=owner,
            company=registration,
            **create_request.model_dump(),
            **kwargrs,
        )
        return self

    @classmethod
    async def gen_registration(cls, owner: str, **kwargs):
        return await super().gen_registration(owner, **kwargs)
