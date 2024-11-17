from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from bson import ObjectId
from session import db


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
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            registration=registration,
            owner=owner,
            **create_request.model_dump(),
            **kwargrs,
        )
        return self

    @abstractmethod
    async def gen_registration(cls, owner: str, **kwargs):
        pass

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
        cls, pagination_request: PaginationRequest
    ) -> "PaginatedResponse":
        find = {}
        if pagination_request.query:
            regex = {"$regex": pagination_request.value, "$options": "i"}
            find = {
                "$or": [
                    {"$text": {"$search": pagination_request.value}},
                    {pagination_request.query: regex},
                ]
            }
        objs = (
            db[cls.table_name()]
            .find(find)
            .skip(PaginationRequest.skip)
            .limit(PaginationRequest.limit)
        )
        total = await db[cls.table_name()].count_documents(find)
        results = [
            cls(
                id=obj["_id"],
                created_at=obj["created_at"],
                updated_at=obj["updated_at"],
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

    @classmethod
    async def delete(cls, registration: str) -> ActionResponse:
        await db[cls.table_name()].delete_one({"registration": registration})
        return ActionResponse(
            action="delete", message=f"{cls.__name__} deleted successfully"
        )


T = TypeVar("T", bound=BaseClass)


class PaginatedResponse(BaseModel, Generic[T]):
    pagination: Pagination
    results: list[T]
