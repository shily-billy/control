from telegram import Update
from telegram.ext import ContextTypes

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show help message
    """
    help_text = """
📚 **راهنمای استفاده**

**دستورات موجود:**

/start - شروع ربات
/products - مشاهده محصولات
/orders - سفارشات من
/help - راهنما

**چگونه خرید کنم؟**

1️⃣ روی /products کلیک کنید
2️⃣ محصول مورد نظر را انتخاب کنید
3️⃣ دکمه "سفارش محصول" را بزنید
4️⃣ فرم سفارش را تکمیل کنید

📞 **پشتیبانی:** @dotshop_support
    """
    
    await update.message.reply_text(help_text, parse_mode="Markdown")