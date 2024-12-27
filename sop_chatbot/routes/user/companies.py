from typing import Annotated

from fastapi import Depends
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter

from models.companies import Company
from models.users import User
from routes.dependencies import session_dependency

router = APIRouter(prefix='/companies', tags=['Companies'])


@router.get('/', response_class=ORJSONResponse, response_model=Company)
async def get_my_company(
    session: Annotated[User, Depends(session_dependency)],
):
    company = await Company.get(session.company)
    return company.json()
