from abc import ABC, abstractmethod
from typing import Annotated, Any, Generic, Type

from fastapi import Depends, HTTPException, Path
from routes.mixins import (
    T,
    ActionResponse,
    PaginatedResponse,
    PaginationRequest,
)
from services.auth import oauth_scheme, Auth


def session_dependency(token: Annotated[str, Depends(oauth_scheme)]):
    payload = Auth().decode_jwt(token)
    # Do something with the payload
    pass


def admin_dependency(token: Annotated[str, Depends(oauth_scheme)]):
    session = session_dependency(token)
    # Do something with the session
    pass


class Dependency(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass


class ListDependency(Dependency, Generic[T]):
    """
    Dependency to get a list of objects.
    """

    def __init__(self, cls: Type[T]) -> None:
        self.cls = cls

    async def __call__(
        self,
        skip: Annotated[int, Path(description="The number of objects to skip.")] = 0,
        limit: Annotated[
            int, Path(description="The number of objects to return.")
        ] = 10,
        query: Annotated[
            str, Path(description="The query to filter the objects.")
        ] = None,
        value: Annotated[
            Any, Path(description="The value to filter the objects.")
        ] = None,
    ) -> PaginatedResponse:
        pagination = PaginationRequest(skip=skip, limit=limit, query=query, value=value)
        return await self.cls.get_all(pagination)


class ObjectDependency(Dependency, Generic[T]):
    """
    Dependency to get an object by id.
    """

    def __init__(self, cls: Type[T]) -> None:
        self.cls = cls

    async def __call__(
        self,
        id: Annotated[
            str,
            Path(
                min_length=24,
                max_length=24,
                description="The id of the object being fetched.",
            ),
        ],
    ) -> T:
        obj = await self.cls.get(id)

        if obj is None:
            raise HTTPException(
                status_code=404, detail=f"{self.cls.__name__} does not exist"
            )

        return obj


class DeleteDependency(Dependency, Generic[T]):
    """
    Dependency to delete an object.
    """

    def __init__(self, object_dependency: ObjectDependency[T]) -> None:
        self.object_dependency = object_dependency

    def _get_object_dependency(self) -> ObjectDependency[T]:
        return self.object_dependency

    async def __call__(
        self, object: Annotated[T, Depends(_get_object_dependency)]
    ) -> ActionResponse:
        return await object.delete()
