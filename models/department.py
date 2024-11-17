from typing import Annotated
from pydantic import Field
from models.mixins import BaseClass, BaseRequest
from session import db


class CreateDepartmentRequest(BaseRequest):
    name: Annotated[str, Field(description="The name of the company")]
    description: Annotated[str, Field(description="The description of the company")]


class Department(BaseClass, CreateDepartmentRequest):
    users: Annotated[
        list[str], Field(description="The list of users in the company")
    ] = []

    async def gen_registration(cls, owner: str, **kwargs):
        registration = "002."
        owner_part = owner.split(".")[1]
        registration += owner_part + "."
        all_companies = await db[cls.table_name()].count_documents({"owner": owner})
        registration += str(all_companies + 1).zfill(3)
        return registration
