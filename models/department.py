from typing import Annotated
from pydantic import Field
from models.mixins import BaseClass, BaseRequest


class CreateDepartmentRequest(BaseRequest):
    name: Annotated[str, Field(description="The name of the company")]
    description: Annotated[str, Field(description="The description of the company")]


class Department(BaseClass, CreateDepartmentRequest):
    users: Annotated[
        list[str], Field(description="The list of users in the company")
    ] = []

    @classmethod
    async def gen_registration(cls, owner: str, **kwargs):
        return await super().gen_registration(owner, **kwargs)
