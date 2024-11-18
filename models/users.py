from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Annotated
from pydantic import EmailStr, Field
from models.mixins import BaseClass, BaseRequest
from services.auth import Auth
from session import db


class UserRoles(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class CreateUserRequest(BaseRequest):
    name: Annotated[str, Field(description="The name of the user")]
    department: Annotated[str, Field(description="The department of the user")]
    password: Annotated[str, Field(description="The password of the user")]
    role: Annotated[UserRoles, Field(description="The role of the user")] = (
        UserRoles.USER
    )


class CreateAdminRequest(CreateUserRequest):
    department: Annotated[str, Field(description="The department of the user")] = (
        "administration"
    )
    email: Annotated[
        EmailStr,
        Field(
            description="The email of the user. Only the owner of the plan has their email registrationed"
        ),
    ] = None
    role: Annotated[UserRoles, Field(description="The role of the user")] = (
        UserRoles.ADMIN
    )


class CommonUserRequest(BaseRequest):
    company: Annotated[str, Field(description="The company of the user")]


class BaseUser(BaseClass, CreateUserRequest, ABC):
    @classmethod
    def table_name(cls):
        return "users"

    @classmethod
    async def create(cls, create_request: CreateUserRequest, owner: str | None = None):
        created_at = datetime.now()
        updated_at = datetime.now()
        registration, updated_owner = await cls.gen_registration(owner)
        create_request.password = Auth.encrypt_password(create_request.password)
        id = (
            await db[cls.table_name()].insert_one(
                {
                    **create_request.mongo(),
                    "owner": updated_owner,
                    "registration": registration,
                    "created_at": created_at,
                    "updated_at": updated_at,
                }
            )
        ).inserted_id
        self = cls(
            id=str(id),
            registration=registration,
            owner=updated_owner,
            created_at=created_at,
            updated_at=updated_at,
            **create_request.model_dump(),
        )
        return self

    @classmethod
    @abstractmethod
    async def gen_registration(cls, owner: str | None) -> tuple[str, str]:
        pass

    @classmethod
    async def get(cls, registration: str):
        obj = await db[cls.table_name()].find_one({"registration": registration})
        if obj:
            if not obj.get("company"):
                obj["company"] = ""
            return cls(
                id=str(obj["_id"]),
                **obj,
            )
        return None

    def json(self) -> dict:
        dump = super().json()
        dump.pop("password", None)
        return dump

    def mongo(self) -> dict:
        dump = super().mongo()
        dump.pop("password", None)
        return dump

    def verify_password(self, password: str) -> bool:
        return self.password == Auth.encrypt_password(password)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRoles.ADMIN

    @property
    def is_manager(self) -> bool:
        return self.role == UserRoles.MANAGER or self.is_admin


class UserResponse(BaseClass):
    registration: Annotated[str, Field(description="The registration of the user")]
    owner: Annotated[str, Field(description="The owner of the user")]
    name: Annotated[str, Field(description="The name of the user")]
    department: Annotated[str, Field(description="The department of the user")]
    company: Annotated[str | None, Field(description="The company of the user")] = None
    role: Annotated[UserRoles, Field(description="The role of the user")] = (
        UserRoles.USER
    )

    def gen_registration(cls, owner: EmailStr, **kwargs):
        return super().gen_registration(owner, **kwargs)


class AdminResponse(UserResponse):
    email: Annotated[
        EmailStr,
        Field(
            description="The email of the user. Only the owner of the plan has their email registrationed"
        ),
    ]


class User(BaseUser, CommonUserRequest):
    @classmethod
    async def gen_registration(cls, owner: str) -> tuple[str, str]:
        pipeline = [
            {"$match": {"owner": owner}},
            {
                "$project": {
                    "registration": {
                        "$toInt": {
                            "$substr": [
                                "$registration",
                                {
                                    "$add": [
                                        {"$indexOfBytes": ["$registration", "."]},
                                        1,
                                    ]
                                },
                                {
                                    "$subtract": [
                                        {"$strLenCP": "$registration"},
                                        {
                                            "$add": [
                                                {
                                                    "$indexOfBytes": [
                                                        "$registration",
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
            {"$sort": {"registration": -1}},
            {"$limit": 1},
        ]
        result = await db.users.aggregate(pipeline).to_list(length=1)
        highest_registration = result[0]["registration"]
        return ".".join(owner.split(".")[0:2]) + "." + str(highest_registration).zfill(
            3
        ), owner


class Admin(BaseUser, CreateAdminRequest):
    @classmethod
    async def gen_registration(cls, owner: None) -> tuple[str, str]:
        registration = "001."
        all_users = await db[cls.table_name()].count_documents({})
        registration += str(all_users + 1).zfill(4)
        registration += ".000"
        return registration, registration


class UpdateUserRequest(BaseRequest):
    name: Annotated[str | None, Field(description="The name of the user")] = None
    department: Annotated[
        str | None, Field(description="The department of the user")
    ] = None
    company: Annotated[str | None, Field(description="The company of the user")] = None
    role: Annotated[UserRoles | None, Field(description="The role of the user")] = None
