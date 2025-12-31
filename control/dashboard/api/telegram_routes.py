"""Telegram webhook router.

Exposes endpoint used by Telegram to deliver updates.
"""

from fastapi import APIRouter, Request
from telegram import Update

from control.integrations.telegram_bot import build_application

router = APIRouter(prefix="/telegram", tags=["telegram"])

_application = None


def get_app():
    global _application
    if _application is None:
        _application = build_application()
    return _application


@router.post("/webhook")
async def telegram_webhook(request: Request):
    app = get_app()
    payload = await request.json()
    update = Update.de_json(payload, app.bot)
    await app.process_update(update)
    return {"ok": True}
