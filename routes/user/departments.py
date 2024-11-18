from typing import Annotated
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter

from models.departments import Department
from models.mixins import PaginatedResponse
from routes.dependencies import ListDependency, ObjectDependency


router = APIRouter(prefix="/departments", tags=["Departments"])
department_dependency = ObjectDependency(Department)
departments_dependency = ListDependency(Department)


@router.get(
    "/", response_model=PaginatedResponse[Department], response_class=ORJSONResponse
)
async def get_my_departments(
    department: Annotated[PaginatedResponse[Department], departments_dependency],
):
    return department.json()
