from fastapi import APIRouter

from .admin.admin import router as admin_router
from .admin_portal.admin_portal import router as admin_portal_router
from .auth import router as auth_router
from .manager.managers import router as managers_router
from .user.current_user import router as users_router

router = APIRouter(prefix='/api')
router.include_router(auth_router)
router.include_router(admin_router)
router.include_router(users_router)
router.include_router(managers_router)
router.include_router(admin_portal_router)
