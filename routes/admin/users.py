from fastapi.routing import APIRouter


router = APIRouter(prefix="/users", tags=["Admin: Users"])
