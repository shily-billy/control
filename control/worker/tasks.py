"""Celery tasks"""

import asyncio

from control.worker.celery_app import celery_app
from control.catalog.vendor_sync import sync_all_vendors


@celery_app.task(name="control.ping")
def ping():
    return {"pong": True}


@celery_app.task(name="control.sync_vendors")
def sync_vendors():
    # Celery task is sync; run async sync function in its own loop
    result = asyncio.run(sync_all_vendors())
    return {"synced": result}
