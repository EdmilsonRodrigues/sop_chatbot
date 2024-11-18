from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from bson import ObjectId
from session import db


CLASS_MAPPING = {
    "User": "001",
    "Company": "002",
    "Department": "003",
}


class ActionResponse(BaseModel):
    action: str
    message: str


class PaginationRequest(BaseModel):
    skip: int = 0
    limit: int = 10
    query: str | None = None
    value: Any = None


class Pagination(BaseModel):
    page: int = 1
    limit: int = 10
    total: int = 0


class BaseRequest(BaseModel, ABC):
    def mongo(self):
        dump = self.model_dump()
        dump.pop("id", None)
        for key, value in dump.items():
            if isinstance(value, ObjectId):
                dump[key] = str(value)
            elif isinstance(value, BaseClass):
                dump[key] = value.mongo()
            elif isinstance(value, Enum):
                dump[key] = value.value
        return dump


class BaseClass(BaseRequest, ABC):
    id: Annotated[
        str, Field(min_length=24, max_length=24, description="The id of the object")
    ]
    registration: Annotated[
        str, Field(description="The registration string of the object")
    ]
    created_at: Annotated[
        datetime, Field(description="The date and time the object was created")
    ]
    updated_at: Annotated[
        datetime, Field(description="The date and time the object was last updated")
    ]
    owner: Annotated[str, Field(description="The owner of the account")]
    company: Annotated[str, Field(description="The company of the user")]

    @classmethod
    def table_name(cls):
        return cls.__name__.lower() + "s"

    @classmethod
    def __get_json_value(cls, value):
        if isinstance(value, Enum):
            return value.value
        elif isinstance(value, BaseClass):
            return value.json()
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, list):
            return [cls.__get_json_value(value) for i in value]
        return value

    def json(self):
        dump = self.model_dump()
        for key, value in dump.items():
            dump[key] = self.__get_json_value(value)
        return dump

    async def update(self, data: dict):
        self.updated_at = datetime.now()
        for key, value in data.items():
            if value is not None:
                setattr(self, key, value)
        await db[self.table_name()].update_one(
            {"_id": ObjectId(self.id)}, {"$set": self.mongo()}
        )
        return self

    @classmethod
    async def create(cls, create_request: BaseRequest, owner: str, **kwargrs):
        created_at = datetime.now()
        updated_at = datetime.now()
        registration = await cls.gen_registration(owner)
        id = (
            await db[cls.table_name()].insert_one(
                {
                    **create_request.mongo(),
                    "registration": registration,
                    "owner": owner,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    **kwargrs,
                }
            )
        ).inserted_id
        self = cls(
            id=str(id),
            created_at=created_at,
            updated_at=updated_at,
            registration=registration,
            owner=owner,
            **create_request.model_dump(),
            **kwargrs,
        )
        return self

    @classmethod
    @abstractmethod
    async def gen_registration(cls, owner: str, **kwargs):
        registration = CLASS_MAPPING[cls.__name__] + "."
        owner_part = owner.split(".")[1]
        registration += owner_part + "."
        all_companies = await db[cls.table_name()].count_documents({"owner": owner})
        registration += str(all_companies + 1).zfill(3)
        return registration

    @classmethod
    async def get(cls, registration: str):
        obj = await db[cls.table_name()].find_one({"registration": registration})
        if obj:
            return cls(
                id=str(obj["_id"]),
                **obj,
            )
        return None

    @classmethod
    async def get_by_field(cls, key: str, value: Any):
        obj = await db[cls.table_name()].find_one({key: value})
        if obj:
            return cls(
                id=str(obj["_id"]),
                **obj,
            )
        return None

    @classmethod
    async def get_all(
        cls,
        pagination_request: PaginationRequest,
        owner: str,
        user_registration: str | None = None,
        **kwargs,
    ) -> "PaginatedResponse":
        find = {"owner": owner}
        if user_registration is not None:
            user = await db.users.find_one({"registration": user_registration})
            if user is None:
                return PaginatedResponse(pagination=Pagination(), results=[])
            find["company"] = user["company"]
            find["users"] = {"$in": [user_registration]}
            if cls.table_name() in user:
                field = user[cls.table_name()]
                if isinstance(field, list):
                    find[cls.__name__.lower()] = {"$in": field}
        if pagination_request.query:
            regex = {"$regex": pagination_request.value, "$options": "i"}
            find.update(
                {
                    "$or": [
                        {"$text": {"$search": pagination_request.value}},
                        {pagination_request.query: regex},
                    ]
                }
            )
        objs = (
            db[cls.table_name()]
            .find(find)
            .skip(pagination_request.skip)
            .limit(pagination_request.limit)
        )
        total = await db[cls.table_name()].count_documents(find)
        results = [
            cls(
                id=str(obj["_id"]),
                **obj,
            )
            async for obj in objs
        ]
        pagination = Pagination(
            page=pagination_request.skip + 1,
            limit=pagination_request.limit,
            total=total,
        )
        return PaginatedResponse(pagination=pagination, results=results)

    async def delete(self) -> ActionResponse:
        await db[self.table_name()].delete_one({"registration": self.registration})
        return ActionResponse(
            action="delete", message=f"{self.__class__.__name__} deleted successfully"
        )


T = TypeVar("T", bound=BaseClass)


class PaginatedResponse(BaseModel, Generic[T]):
    pagination: Pagination
    results: list[T]

    def json(self):
        return {
            "pagination": self.pagination.model_dump(),
            "results": [result.json() for result in self.results],
        }
