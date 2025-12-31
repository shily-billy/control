"""Celery tasks"""

from control.worker.celery_app import celery_app

@celery_app.task(name="control.ping")
def ping():
    return {"pong": True}
