from abc import ABC, abstractmethod
from typing import Annotated, Any, Generic

from fastapi import Depends, HTTPException, Path
from models.mixins import (
    ActionResponse,
    PaginatedResponse,
    PaginationRequest,
    T,
)
from models.users import User
from services.auth import Auth, oauth_scheme


async def session_dependency(
    token: Annotated[str, Depends(oauth_scheme)],
) -> User:
    payload = Auth().decode_jwt(token)
    user = await User.get(payload['user_registration'])
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid token')
    return user


async def admin_dependency(token: Annotated[str, Depends(oauth_scheme)]):
    session = await session_dependency(token)
    if session.is_admin:
        return session
    raise HTTPException(status_code=403, detail='Unauthorized')


async def manager_dependency(token: Annotated[str, Depends(oauth_scheme)]):
    session = await session_dependency(token)
    if session.is_manager:
        return session
    raise HTTPException(status_code=403, detail='Unauthorized')


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

    def __init__(self, cls: type[T]) -> None:
        self.cls = cls

    async def __call__(
        self,
        session_dependency: Annotated[User, Depends(session_dependency)],
        skip: Annotated[
            int, Path(description='The number of objects to skip.')
        ] = 0,
        limit: Annotated[
            int, Path(description='The number of objects to return.')
        ] = 10,
        query: Annotated[
            str, Path(description='The query to filter the objects.')
        ] = None,
        value: Annotated[
            Any, Path(description='The value to filter the objects.')
        ] = None,
    ) -> PaginatedResponse[T]:
        pagination = PaginationRequest(
            skip=skip, limit=limit, query=query, value=value
        )
        return await self.cls.get_all(
            pagination,
            owner=session_dependency.owner,
            user_registration=session_dependency.registration,
        )


class AdminListDependency(ListDependency[T]):
    """
    Dependency to get a list of objects.
    """

    async def __call__(
        self,
        session_dependency: Annotated[User, Depends(admin_dependency)],
        skip: Annotated[
            int, Path(description='The number of objects to skip.')
        ] = 0,
        limit: Annotated[
            int, Path(description='The number of objects to return.')
        ] = 10,
        query: Annotated[
            str, Path(description='The query to filter the objects.')
        ] = None,
        value: Annotated[
            Any, Path(description='The value to filter the objects.')
        ] = None,
    ) -> PaginatedResponse[T]:
        pagination = PaginationRequest(
            skip=skip, limit=limit, query=query, value=value
        )
        return await self.cls.get_all(
            pagination, owner=session_dependency.registration
        )


class ObjectDependency(Dependency, Generic[T]):
    """
    Dependency to get an object by id.
    """

    def __init__(
        self,
        cls: type[T],
        foreign_key: str | None = None,
        relational_list: str | None = None,
    ) -> None:
        self.cls = cls
        self.foreign_key = foreign_key
        self.relational_list = relational_list

    async def __call__(
        self,
        session: Annotated[User, Depends(session_dependency)],
        registration: Annotated[
            str,
            Path(
                description='The registration of the object being fetched.',
            ),
        ],
    ) -> T:
        obj = await self.cls.get(registration)

        if obj is None:
            raise HTTPException(
                status_code=404, detail=f'{self.cls.__name__} does not exist'
            )

        users: list[str] = getattr(obj, 'users', None)
        authorized = False

        if users is not None:
            if session.registration in users:
                authorized = True

        if self.foreign_key:
            if getattr(obj, self.foreign_key, None) == session.registration:
                authorized = True
            elif getattr(session, self.foreign_key, None) == obj.registration:
                authorized = True

        if self.relational_list:
            if session.registration in getattr(obj, self.relational_list, []):
                authorized = True
            elif obj.registration in getattr(
                session, self.relational_list, []
            ):
                authorized = True

        if not authorized:
            raise HTTPException(status_code=403, detail='Unauthorized')

        return obj


class AdminObjectDependency(ObjectDependency[T]):
    """
    Dependency to get an object by id.
    """

    async def __call__(
        self,
        session: Annotated[User, Depends(admin_dependency)],
        registration: Annotated[
            str,
            Path(
                description='The registration of the object being fetched.',
            ),
        ],
    ) -> T:
        obj = await self.cls.get(registration)

        if obj is None:
            raise HTTPException(
                status_code=404, detail=f'{self.cls.__name__} does not exist'
            )

        if obj.owner != session.registration:
            raise HTTPException(status_code=403, detail='Unauthorized')

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
