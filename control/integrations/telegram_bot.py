"""Telegram bot service (webhook)

Runs alongside FastAPI. Telegram sends updates to /telegram/webhook.
"""

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from control.integrations.telegram_catalog import cmd_catalog, cmd_product, cmd_publish_catalog

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


def build_application() -> Application:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    app = Application.builder().token(BOT_TOKEN).build()

    async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.effective_message.reply_text("سلام! ربات کنترل فعال شد.\nدستورات: /catalog /product")

    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.effective_message.reply_text(
            "دستورات:\n"
            "/catalog - نمایش کاتالوگ\n"
            "/product <SKU> - نمایش محصول\n"
            "/publish_catalog - انتشار کاتالوگ در کانال (ادمین لازم است)"
        )

    async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Minimal auto-reply for direct/group chats
        if update.message and update.message.text:
            await update.effective_message.reply_text("پیام دریافت شد. برای کاتالوگ: /catalog")

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))

    # Catalog commands
    app.add_handler(CommandHandler("catalog", cmd_catalog))
    app.add_handler(CommandHandler("product", cmd_product))
    app.add_handler(CommandHandler("publish_catalog", cmd_publish_catalog))

    # Generic auto response
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    return app
