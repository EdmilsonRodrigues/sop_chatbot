from fastapi import APIRouter, HTTPException

from config import DEBUG


router = APIRouter(prefix="/companies", tags=["Admin: Companies"])


@router.get("/")
async def get_companies():
    if not DEBUG:
        raise HTTPException(status_code=403, detail="Forbidden")
    return [{"name": "Company One"}, {"name": "Company Two"}]


@router.get("/{register}")
async def get_company():
    return {"name": "Company One"}


@router.post("/")
async def create_company():
    return {"name": "Company One"}


@router.put("/{register}")
async def update_company():
    return {"name": "Company One"}


@router.delete("/{register}")
async def delete_company():
    if not DEBUG:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"name": "Company One"}
