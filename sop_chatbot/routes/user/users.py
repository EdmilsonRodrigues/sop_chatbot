from typing import Annotated

from bson import ObjectId
from fastapi import Body, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter
from models.users import User, UserResponse
from routes.dependencies import session_dependency
from services.auth import Auth
from session import db

router = APIRouter(tags=['Users'])


@router.get('/', response_model=UserResponse, response_class=ORJSONResponse)
async def get_me(session: Annotated[User, Depends(session_dependency)]):
    return session.json()


@router.put('/', response_model=UserResponse, response_class=ORJSONResponse)
async def update_me(
    session: Annotated[User, Depends(session_dependency)],
    name: Annotated[str, Body(description='The new name', embed=True)],
):
    session = await session.update({'name': name})
    return session.json()


@router.put(
    '/password', response_model=UserResponse, response_class=ORJSONResponse
)
async def update_my_password(
    session: Annotated[User, Depends(session_dependency)],
    old_password: Annotated[
        str, Body(description='The old password', embed=True)
    ],
    new_password: Annotated[
        str, Body(description='The new password', embed=True)
    ],
):
    if not session.verify_password(old_password):
        raise HTTPException(
            status_code=403,
            detail='Old password is incorrect',
        )
    await db[session.table_name()].update_one(
        {'_id': ObjectId(session.id)},
        {'$set': {'password': Auth.encrypt_password(new_password)}},
    )
    return session.json()
