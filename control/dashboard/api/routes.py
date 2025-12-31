"""API routes"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"name": "control", "status": "running"}
