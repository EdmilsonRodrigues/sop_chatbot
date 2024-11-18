from fastapi import APIRouter

from routes.auth import router as auth_router
from routes.admin.admin import router as admin_router
from routes.user.current_user import router as users_router
from routes.manager.managers import router as managers_router
from routes.admin_portal.admin_portal import router as admin_portal_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(admin_router)
router.include_router(users_router)
router.include_router(managers_router)
router.include_router(admin_portal_router)
