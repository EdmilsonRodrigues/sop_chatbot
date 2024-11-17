from datetime import datetime
from enum import Enum
from typing import Annotated
from pydantic import EmailStr, Field
from models.mixins import BaseClass, BaseRequest
from session import db


class UserRoles(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class CreateUserRequest(BaseRequest):
    name: Annotated[str, Field(description="The name of the user")]
    department: Annotated[
        str | None, Field(description="The department of the user")
    ] = None
    company: Annotated[str | None, Field(description="The company of the user")] = None
    email: Annotated[
        EmailStr | None,
        Field(
            description="The email of the user. Only the owner of the plan has their email registered"
        ),
    ] = None
    password: Annotated[str, Field(description="The password of the user")]
    role: Annotated[UserRoles, Field(description="The role of the user")] = (
        UserRoles.USER
    )


class User(BaseClass, CreateUserRequest):
    owner: Annotated[str, Field(description="The owner of the user account")]

    @classmethod
    async def create(cls, create_request: CreateUserRequest, owner: str | None = None):
        created_at = datetime.now()
        updated_at = datetime.now()
        if owner is None:
            register = "001."
            all_users = await db[cls.table_name()].count_documents()
            register += str(all_users + 1).zfill(4)
            register += ".000"
            owner = register
        else:
            register = await cls.gen_register(create_request)
        id = (
            await db[cls.table_name()].insert_one(
                {
                    **create_request.mongo(),
                    "owner": owner,
                    "register": register,
                    "created_at": created_at,
                    "updated_at": updated_at,
                }
            )
        ).inserted_id
        self = cls(
            id=id,
            register=register,
            owner=owner,
            created_at=created_at,
            updated_at=updated_at,
            **create_request.model_dump(),
        )
        return self

    async def gen_register(cls, create_request: BaseRequest, owner: str):
        pipeline = [
            {"$match": {"owner": owner}},
            {
                "$project": {
                    "register": {
                        "$toInt": {
                            "$substr": [
                                "$register",
                                {
                                    "$add": [
                                        {"$indexOfBytes": ["$register", "."]},
                                        1,
                                    ]
                                },
                                {
                                    "$subtract": [
                                        {"$strLenCP": "$register"},
                                        {
                                            "$add": [
                                                {
                                                    "$indexOfBytes": [
                                                        "$register",
                                                        ".",
                                                    ]
                                                },
                                                1,
                                            ]
                                        },
                                    ]
                                },
                            ]
                        }
                    }
                }
            },
            {"$sort": {"register": -1}},
            {"$limit": 1},
        ]
        result = await db.users.aggregate(pipeline).to_list(length=1)
        highest_register = result[0]["register"]
        return ".".join(owner.split(".")[0:2]) + "." + str(highest_register).zfill(3)

    def json(self) -> dict:
        dump = super().json()
        dump.pop("password", None)
        return dump

    def mongo(self) -> dict:
        dump = super().mongo()
        dump.pop("password", None)
        return dump


class UpdateUserRequest(BaseRequest):
    name: Annotated[str | None, Field(description="The name of the user")] = None
    department: Annotated[
        str | None, Field(description="The department of the user")
    ] = None
    company: Annotated[str | None, Field(description="The company of the user")] = None
    role: Annotated[UserRoles | None, Field(description="The role of the user")] = None
