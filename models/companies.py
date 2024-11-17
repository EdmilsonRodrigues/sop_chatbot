from typing import Annotated
from pydantic import Field
from models.mixins import BaseClass, BaseRequest
from session import db


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

    async def gen_register(cls, owner: str, **kwargs):
        register = "002."
        owner_part = owner.split(".")[1]
        register += owner_part + "."
        all_companies = await db[cls.table_name()].count_documents({"owner": owner})
        register += str(all_companies + 1).zfill(3)
        return register
