from fastapi import APIRouter

from routes.auth import router as auth_router
from routes.admin.admin import router as admin_router
from routes.companies import router as companies_router
from routes.departments import router as departments_router
from routes.users import router as users_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(admin_router)
router.include_router(users_router)
router.include_router(companies_router)
router.include_router(departments_router)
