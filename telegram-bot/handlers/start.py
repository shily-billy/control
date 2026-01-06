from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os

SHOP_NAME = os.getenv("SHOP_NAME", "فروشگاه نقطه")

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for /start command
    """
    user = update.effective_user
    
    welcome_text = f"""
👋 سلام {user.first_name} عزیز!

خوش اومدید به **{SHOP_NAME}** 🛍️

اینجا می‌تونید:
• محصولات رو مشاهده کنید
• سفارش ثبت کنید
• سفارشات رو پیگیری کنید

برای شروع یکی از دکمه‌ها رو انتخاب کنید:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🛍️ محصولات", callback_data="products"),
            InlineKeyboardButton("📝 سفارشات من", callback_data="my_orders")
        ],
        [
            InlineKeyboardButton("📞 تماس با ما", callback_data="contact"),
            InlineKeyboardButton("❓ راهنما", callback_data="help")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )