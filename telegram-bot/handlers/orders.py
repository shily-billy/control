from telegram import Update
from telegram.ext import ContextTypes

async def orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show user's orders
    """
    await update.message.reply_text(
        "📝 سفارشات شما:\n\nدر حال حاضر سفارشی ندارید."
    )