import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from handlers.start import start_handler
from handlers.products import products_handler, product_detail_handler
from handlers.orders import orders_handler
from handlers.help import help_handler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("توکن ربات تلگرام تنظیم نشده است")

def main():
    """Start the bot."""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("products", products_handler))
    application.add_handler(CommandHandler("orders", orders_handler))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(product_detail_handler, pattern="^product_"))
    application.add_handler(CallbackQueryHandler(products_handler, pattern="^products$"))
    
    # Start the bot
    logger.info("🚀 DOT SHOP Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()