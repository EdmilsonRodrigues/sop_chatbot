from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from models.department import Department, CreateDepartmentRequest
from models.mixins import PaginatedResponse
from models.users import User
from routes.dependencies import (
    AdminListDependency,
    AdminObjectDependency,
    DeleteDependency,
    admin_dependency,
)


router = APIRouter(prefix="/departments", tags=["Admin: Departments"])
departments_dependency = AdminListDependency(Department)
department_dependency = AdminObjectDependency(Department)
delete_dependency = DeleteDependency(department_dependency)


@router.get(
    "/", response_model=PaginatedResponse[Department], response_class=ORJSONResponse
)
async def get_departments(
    departments: Annotated[
        PaginatedResponse[Department], Depends(departments_dependency)
    ],
):
    return departments.json()


@router.post("/", response_model=Department, response_class=ORJSONResponse)
async def create_department(
    request: CreateDepartmentRequest,
    session: Annotated[User, Depends(admin_dependency)],
):
    department = await Department.create(
        create_request=request,
        owner=session.registration,
    )
    return department.json()


@router.get("/{registration}", response_model=Department, response_class=ORJSONResponse)
async def get_department(
    department: Annotated[Department, Depends(department_dependency)],
):
    return department.json()


@router.put("/{registration}", response_model=Department, response_class=ORJSONResponse)
async def update_department(
    request: CreateDepartmentRequest,
    department: Annotated[Department, Depends(department_dependency)],
):
    department = await department.update(request.model_dump())
    return department.json()


@router.delete("/{registration}")
async def delete_department(
    department: Annotated[Department, Depends(delete_dependency)],
):
    return await department.delete()
