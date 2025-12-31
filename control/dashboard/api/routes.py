"""API routes"""

from fastapi import APIRouter
from control.dashboard.api.telegram_routes import router as telegram_router
from control.worker.tasks import sync_vendors

router = APIRouter()

@router.get("/")
async def root():
    return {"name": "control", "status": "running"}

@router.post("/catalog/sync")
async def catalog_sync():
    job = sync_vendors.delay()
    return {"task_id": job.id, "status": "queued"}

router.include_router(telegram_router)
