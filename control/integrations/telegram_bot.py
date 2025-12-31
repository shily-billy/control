"""Telegram bot service (webhook)

Runs alongside FastAPI. Telegram sends updates to /telegram/webhook.
"""

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


def build_application() -> Application:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    app = Application.builder().token(BOT_TOKEN).build()

    async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("سلام! ربات کنترل فعال شد. پیام بده تا پاسخ خودکار بگیری.")

    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("دستورات: /start /help")

    async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text if update.message else ""
        await update.message.reply_text(f"دریافت شد: {text}")

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    return app
