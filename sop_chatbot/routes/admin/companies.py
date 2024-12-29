from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from ...models.companies import (
    Company,
    CreateCompanyRequest,
    UpdateCompanyRequest,
)
from ...models.mixins import PaginatedResponse
from ..dependencies import (
    AdminListDependency,
    AdminObjectDependency,
    DeleteDependency,
)

router = APIRouter(prefix='/companies', tags=['Admin: Companies'])
companies_dependency = AdminListDependency(Company)
company_dependency = AdminObjectDependency(Company)
delete_dependency = DeleteDependency(company_dependency)


@router.get(
    '/',
    response_model=PaginatedResponse[Company],
    response_class=ORJSONResponse,
)
async def get_companies(
    companies: Annotated[
        PaginatedResponse[Company], Depends(companies_dependency)
    ],
):
    return companies.json()


@router.get(
    '/{registration}', response_model=Company, response_class=ORJSONResponse
)
async def get_company(
    company: Annotated[Company, Depends(company_dependency)],
):
    return company.json()


@router.put(
    '/{registration}', response_model=Company, response_class=ORJSONResponse
)
async def update_company(
    request: CreateCompanyRequest,
    company: Annotated[Company, Depends(company_dependency)],
):
    company = await company.update(request.model_dump())
    return company.json()


@router.patch(
    '/{registration}', response_model=Company, response_class=ORJSONResponse
)
async def partial_update_company(
    request: UpdateCompanyRequest,
    company: Annotated[Company, Depends(company_dependency)],
):
    company = await company.update(request.model_dump(exclude_unset=True))
    return company.json()
