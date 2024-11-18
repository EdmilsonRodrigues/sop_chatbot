from typing import Annotated
from pydantic import Field
from models.mixins import BaseClass, BaseRequest


class CreateCompanyRequest(BaseRequest):
    name: Annotated[str, Field(description="The name of the company")]
    description: Annotated[str, Field(description="The description of the company")]


class Company(BaseClass, CreateCompanyRequest):
    users: Annotated[
        list[str], Field(description="The list of users in the company")
    ] = []

    @classmethod
    def table_name(cls):
        return "companies"

    @classmethod
    async def gen_registration(cls, owner: str, **kwargs):
        return await super().gen_registration(owner, **kwargs)
