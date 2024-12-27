from fastapi import APIRouter
from routes.manager.companies import router as companies_router
from routes.manager.departments import router as departments_router
from routes.manager.users import router as users_router

router = APIRouter(prefix='/managers', tags=['Managers'])
router.include_router(users_router)
router.include_router(companies_router)
router.include_router(departments_router)
