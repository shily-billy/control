"""API routes"""

from fastapi import APIRouter
from control.dashboard.api.telegram_routes import router as telegram_router

router = APIRouter()

@router.get("/")
async def root():
    return {"name": "control", "status": "running"}

router.include_router(telegram_router)
