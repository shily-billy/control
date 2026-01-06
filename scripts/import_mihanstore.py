#!/usr/bin/env python3
"""
اسکریپت Import محصولات از میهن استور
"""

import asyncio
import sys
sys.path.append('..')

from backend.integrations.mihanstore import MihanstoreIntegration
from backend.core.database import SessionLocal
from backend.models.product import Product
import os
from dotenv import load_dotenv

load_dotenv('../config/.env')

async def import_products(query: str, limit: int = 50):
    print(f"🔍 جستجو در میهن استور: {query}")
    
    mihanstore = MihanstoreIntegration(
        partner_id=os.getenv('MIHANSTORE_PARTNER_ID', ''),
        commission_rate=0.40
    )
    
    try:
        results = await mihanstore.search_product(query)
        
        if not results:
            print("❌ محصولی یافت نشد")
            return
        
        print(f"✅ {len(results)} محصول پیدا شد (کمیسیون 40%)")
        
        db = SessionLocal()
        imported = 0
        
        for item in results[:limit]:
            existing = db.query(Product).filter(
                Product.platforms.contains({'mihanstore': {'id': item['id']}})
            ).first()
            
            if existing:
                continue
            
            product = Product(
                title=item['title'],
                price=item['price'],
                main_image=item['image'],
                platforms={'mihanstore': item}
            )
            
            db.add(product)
            imported += 1
            print(f"✅ {item['title'][:50]}... - کمیسیون: {item['commission']:,} تومان")
        
        db.commit()
        db.close()
        
        print(f"\n✨ {imported} محصول جدید اضافه شد")
        
    finally:
        await mihanstore.close_session()

if __name__ == "__main__":
    query = input("🔍 جستجو برای چه محصولی؟ ")
    limit = int(input("تعداد (پیش‌فرض 50): ") or "50")
    
    asyncio.run(import_products(query, limit))
