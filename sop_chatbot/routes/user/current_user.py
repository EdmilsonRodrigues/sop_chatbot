from fastapi import APIRouter

from .companies import router as companies_router
from .departments import router as departments_router
from .users import router as users_router

router = APIRouter(prefix='/me', tags=['Current User'])
router.include_router(users_router)
router.include_router(companies_router)
router.include_router(departments_router)
