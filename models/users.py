from enum import Enum
from pydantic import BaseModel, EmailStr
from routes.mixins import BaseClass, BaseRequest


class UserRoles(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class CreateUserRequest(BaseRequest):
    name: str
    register: str
    department: str | None = None
    company: str
    email: EmailStr
    password: str
    role: UserRoles = UserRoles.USER


class User(BaseClass, CreateUserRequest):
    def json(self) -> dict:
        dump = super().json()
        dump.pop("password", None)
        return dump

    def mongo(self) -> dict:
        dump = super().mongo()
        dump.pop("password", None)
        return dump


class UserResponse(BaseModel):
    id: str
    created_at: str
    updated_at: str
    name: str
    register: str
    department: str | None = None
    company: str
    email: EmailStr
    role: UserRoles = UserRoles.USER
