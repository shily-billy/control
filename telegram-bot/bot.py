import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from dotenv import load_dotenv
import httpx

load_dotenv("../config/.env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("NEXT_PUBLIC_API_URL", "http://backend:8000/api")

# ========== دستورات اصلی ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    keyboard = [
        [InlineKeyboardButton("🛍 جستجوی محصول", callback_data="search")],
        [InlineKeyboardButton("📦 سفارشات من", callback_data="my_orders")],
        [InlineKeyboardButton("📊 مقایسه قیمت", callback_data="compare")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
🛒 به **فروشگاه نقطه** خوش آمدید!

🔍 با این ربات می‌توانید:
• جستجو در 10+ فروشگاه همزمان
• مقایسه قیمت لحظه‌ای
• خرید با بهترین قیمت
• پیگیری سفارشات

👇 از منوی زیر انتخاب کنید:
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /help"""
    help_text = """
📖 **راهنمای استفاده**

🔍 **جستجو:**
نام محصول را بنویسید تا در تمام فروشگاه‌ها جستجو شود

📊 **مقایسه:**
بهترین قیمت را برای شما پیدا می‌کنیم

📦 **پیگیری:**
وضعیت سفارشات خود را مشاهده کنید

💬 **پشتیبانی:**
@dotshop_support
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ========== جستجوی محصول ==========

async def search_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """جستجوی محصول در پلتفرم‌ها"""
    query = update.message.text
    
    await update.message.reply_text("🔍 در حال جستجو در تمام فروشگاه‌ها...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/products/search",
                params={"q": query}
            )
            data = response.json()
        
        if data.get("recommended"):
            best = data["recommended"]
            product = best["product"]
            
            result_text = f"""
✅ **بهترین گزینه پیدا شد!**

📦 {product['title']}
💰 قیمت: {product['price']:,} هزار تومان
🏪 فروشگاه: {best['platform']}
💵 کمیسیون شما: {best['commission']:,} تومان
            """
            
            keyboard = [
                [InlineKeyboardButton("🛒 خرید", url=product['url'])],
                [InlineKeyboardButton("🔍 جستجوی جدید", callback_data="search")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                result_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ محصولی یافت نشد. لطفاً دوباره جستجو کنید.")
    
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا در جستجو: {str(e)}")

# ========== کال‌بک‌ها ==========

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت دکمه‌های inline"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "search":
        await query.edit_message_text(
            "🔍 نام محصول مورد نظر خود را بنویسید:"
        )
    
    elif query.data == "my_orders":
        await query.edit_message_text(
            "📦 در حال دریافت سفارشات شما..."
        )
        # TODO: نمایش لیست سفارشات
    
    elif query.data == "compare":
        await query.edit_message_text(
            "📊 نام محصول را برای مقایسه قیمت بنویسید:"
        )
    
    elif query.data == "help":
        await help_command(update, context)

# ========== اجرای ربات ==========

def main():
    """راه‌اندازی ربات"""
    if not BOT_TOKEN:
        print("❌ توکن ربات تنظیم نشده است!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # دستورات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # کال‌بک‌ها
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # پیام‌های متنی (جستجو)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, search_product)
    )
    
    print("✅ ربات فروشگاه نقطه راه‌اندازی شد!")
    application.run_polling()

if __name__ == "__main__":
    main()
