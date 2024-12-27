from typing import Annotated

from bson import ObjectId
from fastapi import Body, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter

from ... import session
from ...models.users import User, UserResponse
from ...services.auth import Auth
from ..dependencies import session_dependency

router = APIRouter(tags=['Users'])


@router.get('/', response_model=UserResponse, response_class=ORJSONResponse)
async def get_me(user_session: Annotated[User, Depends(session_dependency)]):
    return user_session.json()


@router.put('/', response_model=UserResponse, response_class=ORJSONResponse)
async def update_me(
    user_session: Annotated[User, Depends(session_dependency)],
    name: Annotated[str, Body(description='The new name', embed=True)],
):
    user_session = await user_session.update({'name': name})
    return user_session.json()


@router.put(
    '/password', response_model=UserResponse, response_class=ORJSONResponse
)
async def update_my_password(
    user_session: Annotated[User, Depends(session_dependency)],
    old_password: Annotated[
        str, Body(description='The old password', embed=True)
    ],
    new_password: Annotated[
        str, Body(description='The new password', embed=True)
    ],
):
    if not user_session.verify_password(old_password):
        raise HTTPException(
            status_code=403,
            detail='Old password is incorrect',
        )
    await session.db[user_session.table_name()].update_one(
        {'_id': ObjectId(user_session.id)},
        {'$set': {'password': Auth.encrypt_password(new_password)}},
    )
    return user_session.json()
