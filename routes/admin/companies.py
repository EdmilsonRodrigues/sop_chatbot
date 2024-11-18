from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from config import DEBUG
from models.companies import Company, CreateCompanyRequest
from models.mixins import PaginatedResponse
from models.users import User
from routes.dependencies import (
    AdminListDependency,
    AdminObjectDependency,
    DeleteDependency,
    admin_dependency,
)


router = APIRouter(prefix="/companies", tags=["Admin: Companies"])
companies_dependency = AdminListDependency(Company)
company_dependency = AdminObjectDependency(Company)
delete_dependency = DeleteDependency(company_dependency)


@router.get(
    "/", response_model=PaginatedResponse[Company], response_class=ORJSONResponse
)
async def get_companies(
    companies: Annotated[PaginatedResponse[Company], Depends(companies_dependency)],
):
    return companies.json()


@router.post("/", response_model=Company, response_class=ORJSONResponse)
async def create_company(
    request: CreateCompanyRequest, session: Annotated[User, Depends(admin_dependency)]
):
    company = await Company.create(
        create_request=request,
        owner=session.registration,
    )
    return company.json()


@router.get("/{registration}", response_model=Company, response_class=ORJSONResponse)
async def get_company(company: Annotated[Company, Depends(company_dependency)]):
    return company.json()


@router.put("/{registration}", response_model=Company, response_class=ORJSONResponse)
async def update_company(
    request: CreateCompanyRequest,
    company: Annotated[Company, Depends(company_dependency)],
):
    company = await company.update(request.model_dump())
    return company.json()


@router.delete("/{registration}", include_in_schema=False)
async def delete_company(company: Annotated[Company, Depends(delete_dependency)]):
    if not DEBUG:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await company.delete()
