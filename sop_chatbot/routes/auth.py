from typing import Annotated

from fastapi import Body, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from ..models.users import (
    Admin,
    AdminResponse,
    CreateAdminRequest,
    User,
    UserRoles,
)
from ..services.auth import Auth, AuthResponse

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/login', response_model=AuthResponse)
async def login(login: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Login a user to the system. Required the user's registration and password.
    """
    registration = login.username
    password = login.password
    user = await User.get(registration)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    if not user.verify_password(password):
        raise HTTPException(
            status_code=401,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    jwt = Auth.generate_jwt(user.registration)
    return AuthResponse(access_token=jwt)


@router.post(
    '/signup',
    response_model=AdminResponse,
    response_class=ORJSONResponse,
    status_code=201,
)
async def signup(
    create_user_request: Annotated[
        CreateAdminRequest, Body(description='The user to create')
    ],
):
    """
    Signup a user to the system. Required the user's name, email, password, and department.
    """
    create_user_request.role = UserRoles.ADMIN
    user = await Admin.create(create_user_request, owner=None)
    return user.json()


@router.post('/admin/login')
async def admin_login(
    request: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    Login an user to the admin panel. Required the user's email and password.
    """
    email = request.username
    password = request.password
    user = await Admin.get_by_field(key='email', value=email)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    if not user.verify_password(password):
        raise HTTPException(
            status_code=401,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    jwt = Auth.generate_jwt(user.registration)
    return AuthResponse(access_token=jwt)
