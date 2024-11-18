from typing import Annotated
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter

from models.companies import Company
from routes.dependencies import ObjectDependency


router = APIRouter(prefix="/companies", tags=["Companies"])
company_dependency = ObjectDependency(Company)


@router.get("/", response_class=ORJSONResponse, response_model=Company)
async def get_my_company(company: Annotated[Company, company_dependency]):
    return company.json()
