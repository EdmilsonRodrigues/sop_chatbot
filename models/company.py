from typing import Annotated
from pydantic import Field
from models.mixins import BaseClass, BaseRequest
from session import db


class CreateCompanyRequest(BaseRequest):
    name: Annotated[str, Field(description="The name of the company")]
    description: Annotated[str, Field(description="The description of the company")]


class Company(BaseClass, CreateCompanyRequest):
    register: Annotated[
        str, Field(description="The registration number of the company")
    ]
    users: Annotated[
        list[str], Field(description="The list of users in the company")
    ] = []
    owner: Annotated[str, Field(description="The owner of the company account")]

    async def gen_register(cls, create_request: BaseRequest, **kwargs):
        register = "002."
        owner_part = create_request.owner.split(".")[1]
        register += owner_part + "."
        all_companies = await db[cls.table_name()].count_documents()
        register += str(all_companies + 1).zfill(3)
