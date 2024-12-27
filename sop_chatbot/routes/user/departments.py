from typing import Annotated

from fastapi import Depends
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter
from models.departments import Department
from models.mixins import PaginatedResponse
from routes.dependencies import ListDependency, ObjectDependency

router = APIRouter(prefix='/departments', tags=['Departments'])
department_dependency = ObjectDependency(
    Department, relational_list='departments'
)
departments_dependency = ListDependency(Department)


@router.get(
    '/',
    response_model=PaginatedResponse[Department],
    response_class=ORJSONResponse,
)
async def get_my_departments(
    departments: Annotated[
        PaginatedResponse[Department], Depends(departments_dependency)
    ],
):
    return departments.json()


@router.get(
    '/{registration}', response_model=Department, response_class=ORJSONResponse
)
async def get_department(
    department: Annotated[Department, Depends(department_dependency)],
):
    return department.json()
