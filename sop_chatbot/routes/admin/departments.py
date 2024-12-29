import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from ... import session
from ...models.departments import (
    CreateDepartmentRequest,
    Department,
    UpdateDepartmentRequest,
)
from ...models.mixins import ActionResponse, PaginatedResponse
from ...models.users import User
from ..dependencies import (
    AdminListDependency,
    AdminObjectDependency,
    DeleteDependency,
    admin_dependency,
)

router = APIRouter(prefix='/departments', tags=['Admin: Departments'])
departments_dependency = AdminListDependency(Department)
department_dependency = AdminObjectDependency(Department)
delete_dependency = DeleteDependency(department_dependency)


@router.get(
    '/',
    response_model=PaginatedResponse[Department],
    response_class=ORJSONResponse,
)
async def get_departments(
    departments: Annotated[
        PaginatedResponse[Department], Depends(departments_dependency)
    ],
):
    return departments.json()


@router.post('/', response_model=Department, response_class=ORJSONResponse)
async def create_department(
    request: CreateDepartmentRequest,
    session: Annotated[User, Depends(admin_dependency)],
):
    department = await Department.create(
        create_request=request,
        owner=session.registration,
        company=session.company,
    )
    session.departments.append(department.registration)
    await session.update({'departments': session.departments})
    return department.json()


@router.get(
    '/{registration}', response_model=Department, response_class=ORJSONResponse
)
async def get_department(
    department: Annotated[Department, Depends(department_dependency)],
):
    return department.json()


@router.put(
    '/{registration}', response_model=Department, response_class=ORJSONResponse
)
async def update_department(
    request: CreateDepartmentRequest,
    department: Annotated[Department, Depends(department_dependency)],
):
    department = await department.update(request.model_dump())
    return department.json()


@router.patch(
    '/{registration}', response_model=Department, response_class=ORJSONResponse
)
async def partial_update_department(
    request: UpdateDepartmentRequest,
    department: Annotated[Department, Depends(department_dependency)],
):
    department = await department.update(
        request.model_dump(exclude_unset=True)
    )
    return department.json()


@router.delete(
    '/{registration}',
    response_class=ORJSONResponse,
    response_model=ActionResponse,
)
async def delete_department(
    department: Annotated[Department, Depends(department_dependency)],
):
    deleted, _ = await asyncio.gather(
        department.delete(),
        session.db.users.update_many(
            {'departments': {'$in': [department.registration]}},
            {'$pull': {'departments': department.registration}},
        ),
    )
    return deleted.model_dump()
