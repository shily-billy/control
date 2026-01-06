from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
import os

API_URL = os.getenv("NEXT_PUBLIC_API_URL", "http://backend:8000/api")

async def products_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show products list
    """
    query = update.callback_query
    if query:
        await query.answer()
    
    try:
        # Fetch products from API
        response = requests.get(f"{API_URL}/products/", timeout=10)
        products = response.json()
        
        if not products:
            text = "در حال حاضر محصولی موجود نیست."
            keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="start")]]
        else:
            text = f"🛍️ **محصولات ({len(products)} عدد)**\n\nلطفا محصول مورد نظر را انتخاب کنید:"
            
            keyboard = []
            for product in products[:10]:  # Show first 10 products
                keyboard.append([
                    InlineKeyboardButton(
                        f"{product['title']} - {product['final_price']:,} تومان",
                        callback_data=f"product_{product['id']}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="start")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            
    except Exception as e:
        error_text = f"⚠️ خطا در دریافت محصولات: {str(e)}"
        if query:
            await query.edit_message_text(error_text)
        else:
            await update.message.reply_text(error_text)

async def product_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show product details
    """
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split("_")[1])
    
    try:
        # Fetch product details
        response = requests.get(f"{API_URL}/products/{product_id}", timeout=10)
        product = response.json()
        
        # Fetch best platform
        platform_response = requests.get(f"{API_URL}/products/{product_id}/best-platform", timeout=10)
        platform_data = platform_response.json()
        
        best_platform = platform_data.get("best_platform", {})
        
        text = f"""
📦 **{product['title']}**

💰 قیمت: **{product['final_price']:,} تومان**

🏪 بهترین پلتفرم: {best_platform.get('name', '-')}
📊 سود شما: {best_platform.get('commission', 0):,.0f} تومان

وضعیت: {'\u2705 موجود' if product['in_stock'] else '\u274c ناموجود'}
        """
        
        keyboard = [
            [InlineKeyboardButton("🛒 سفارش محصول", callback_data=f"order_{product_id}")],
            [InlineKeyboardButton("🔙 برگشت به لیست", callback_data="products")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        
    except Exception as e:
        await query.edit_message_text(f"⚠️ خطا: {str(e)}")