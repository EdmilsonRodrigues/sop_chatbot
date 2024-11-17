from typing import Annotated
from pydantic import Field
from models.mixins import BaseClass, BaseRequest


class CreateDepartmentRequest(BaseRequest):
    name: Annotated[str, Field(description="The name of the department")]
    description: Annotated[str, Field(description="The description of the company")]
    register: Annotated[
        str, Field(description="The registration number of the company")
    ]
    users: Annotated[list[str], Field(description="The list of users in the company")]


class Company(BaseClass, CreateCompanyRequest):
    pass
