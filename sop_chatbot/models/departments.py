from typing import Annotated

from pydantic import Field

from ..models.mixins import BaseClass, BaseRequest


class CreateDepartmentRequest(BaseRequest):
    name: Annotated[str, Field(description='The name of the company')]
    description: Annotated[
        str, Field(description='The description of the company')
    ]


class UpdateDepartmentRequest(BaseRequest):
    name: Annotated[
        str | None, Field(description='The name of the company')
    ] = None
    description: Annotated[
        str | None, Field(description='The description of the company')
    ] = None


class Department(BaseClass, CreateDepartmentRequest):
    company: Annotated[
        str, Field(description='The company of the user', min_length=12)
    ]

    @classmethod
    def create(
        cls, create_request: BaseRequest, owner: str, company: str, **kwargrs
    ):
        return super().create(
            create_request, owner, company=company, **kwargrs
        )

    @classmethod
    async def gen_registration(cls, owner: str, **kwargs):
        return await super().gen_registration(owner, **kwargs)
