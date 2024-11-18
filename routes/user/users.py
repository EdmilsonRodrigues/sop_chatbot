from typing import Annotated
from fastapi import Body, Depends
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter

from models.users import User
from routes.dependencies import session_dependency
from services.auth import Auth


router = APIRouter(tags=["Users"])


@router.get("/", response_model=User, response_class=ORJSONResponse)
async def get_me(session: Annotated[User, Depends(session_dependency)]):
    return session.json()


@router.put("/", response_model=User, response_class=ORJSONResponse)
async def update_me(
    session: Annotated[User, Depends(session_dependency)],
    name: Annotated[str, Body(description="The new name")],
):
    session = await session.update({"name": name})
    return session.json()


@router.put("/password", response_model=User, response_class=ORJSONResponse)
async def update_my_password(
    session: Annotated[User, Depends(session_dependency)],
    password: Annotated[str, Body(description="The new password")],
):
    session = await session.update({"password": Auth.encrypt_password(password)})
    return session.json()
