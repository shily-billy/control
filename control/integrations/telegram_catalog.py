"""Telegram catalog handlers: direct chat + channel publishing.

Important:
- Bots cannot read arbitrary channel history unless they are admin and Telegram actually delivers updates.
- For catalog publishing, bot can post to a channel if added as admin.
"""

import os
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from control.catalog.store import catalog

CATALOG_CHANNEL_ID = os.getenv("TELEGRAM_CATALOG_CHANNEL_ID", "")


def _product_keyboard(sku: str, buy_url: Optional[str] = None):
    buttons = [[InlineKeyboardButton("مشاهده جزئیات", callback_data=f"product:{sku}")]]
    if buy_url:
        buttons.append([InlineKeyboardButton("خرید", url=buy_url)])
    return InlineKeyboardMarkup(buttons)


async def cmd_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Show list in any chat (private/group) where bot receives the command
    items = catalog.list()
    if not items:
        await update.effective_message.reply_text("کاتالوگ خالی است.")
        return

    lines = ["کاتالوگ محصولات:"]
    for p in items:
        lines.append(f"- {p.sku}: {p.title} | {p.price_toman:,} تومان")
    await update.effective_message.reply_text("\n".join(lines))


async def cmd_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /product P001
    if not context.args:
        await update.effective_message.reply_text("فرمت درست: /product P001")
        return

    sku = context.args[0].strip().upper()
    p = catalog.get(sku)
    if not p:
        await update.effective_message.reply_text("این SKU پیدا نشد.")
        return

    text = f"{p.title}\nSKU: {p.sku}\nقیمت: {p.price_toman:,} تومان\n\n{p.description}".strip()
    await update.effective_message.reply_text(text, reply_markup=_product_keyboard(p.sku, p.buy_url))


async def cmd_publish_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Publishes catalog into a channel (bot must be admin in that channel)
    if not CATALOG_CHANNEL_ID:
        await update.effective_message.reply_text("TELEGRAM_CATALOG_CHANNEL_ID ست نشده.")
        return

    items = catalog.list()
    if not items:
        await update.effective_message.reply_text("کاتالوگ خالی است.")
        return

    for p in items:
        text = f"{p.title}\nSKU: {p.sku}\nقیمت: {p.price_toman:,} تومان\n\n{p.description}".strip()
        await context.bot.send_message(chat_id=CATALOG_CHANNEL_ID, text=text, reply_markup=_product_keyboard(p.sku, p.buy_url))

    await update.effective_message.reply_text("کاتالوگ در کانال منتشر شد.")
