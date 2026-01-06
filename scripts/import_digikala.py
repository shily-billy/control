#!/usr/bin/env python3
"""
اسکریپت Import محصولات از دیجی‌کالا
"""

import asyncio
import sys
sys.path.append('..')

from backend.integrations.digikala import DigikalaIntegration
from backend.core.database import SessionLocal
from backend.models.product import Product
import os
from dotenv import load_dotenv

load_dotenv('../config/.env')

async def import_products(query: str, limit: int = 50):
    """
    Import محصولات از دیجی‌کالا
    """
    print(f"🔍 جستجو برای: {query}")
    
    digikala = DigikalaIntegration(
        affiliate_id=os.getenv('DIGIKALA_AFFILIATE_ID', ''),
        commission_rate=0.12
    )
    
    try:
        results = await digikala.search_product(query)
        
        if not results:
            print("❌ محصولی یافت نشد")
            return
        
        print(f"✅ {len(results)} محصول پیدا شد")
        
        db = SessionLocal()
        imported = 0
        
        for item in results[:limit]:
            # بررسی وجود محصول
            existing = db.query(Product).filter(
                Product.platforms.contains({'digikala': {'id': item['id']}})
            ).first()
            
            if existing:
                print(f"⏭️  قبلاً وجود دارد: {item['title'][:50]}...")
                continue
            
            # ایجاد محصول جدید
            product = Product(
                title=item['title'],
                price=item['price'],
                main_image=item['image'],
                in_stock=item.get('in_stock', True),
                platforms={'digikala': item}
            )
            
            db.add(product)
            imported += 1
            print(f"✅ اضافه شد: {item['title'][:50]}...")
        
        db.commit()
        db.close()
        
        print(f"\n✨ {imported} محصول جدید اضافه شد")
        
    finally:
        await digikala.close_session()

if __name__ == "__main__":
    query = input("🔍 جستجو برای چه محصولی؟ ")
    limit = int(input("تعداد محصولات برای Import (پیش‌فرض 50): ") or "50")
    
    asyncio.run(import_products(query, limit))
