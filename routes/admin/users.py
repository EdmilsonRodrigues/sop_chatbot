from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from models.users import User, CreateUserRequest, UpdateUserRequest
from models.mixins import PaginatedResponse
from routes.dependencies import (
    AdminListDependency,
    AdminObjectDependency,
    DeleteDependency,
    admin_dependency,
)


router = APIRouter(prefix="/users", tags=["Admin: Users"])
users_dependency = AdminListDependency(User)
user_dependency = AdminObjectDependency(User)
delete_dependency = DeleteDependency(user_dependency)


@router.get("/", response_model=PaginatedResponse[User], response_class=ORJSONResponse)
async def get_users(
    users: Annotated[PaginatedResponse[User], Depends(users_dependency)],
):
    return users.json()


@router.post("/", response_model=User, response_class=ORJSONResponse)
async def create_user(
    request: CreateUserRequest, session: Annotated[User, Depends(admin_dependency)]
):
    user = await User.create(
        create_request=request,
        owner=session.registration,
    )
    return user.json()


@router.get("/{registration}", response_model=User, response_class=ORJSONResponse)
async def get_user(user: Annotated[User, Depends(user_dependency)]):
    return user.json()


@router.put("/{registration}", response_model=User, response_class=ORJSONResponse)
async def update_user(
    request: UpdateUserRequest,
    user: Annotated[User, Depends(user_dependency)],
):
    user = await user.update(request.model_dump())
    return user.json()


@router.delete("/{registration}")
async def delete_user(user: Annotated[User, Depends(delete_dependency)]):
    return await user.delete()
