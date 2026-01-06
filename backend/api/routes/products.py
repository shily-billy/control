from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from models.product import Product, Category
from services.platform_selector import PlatformSelector
import asyncio

router = APIRouter()

@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=2),
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    جستجوی محصولات در تمام پلتفرم‌ها یا پلتفرم خاص
    """
    selector = PlatformSelector()
    
    try:
        if platform:
            # جستجو در یک پلتفرم خاص
            if platform not in selector.platforms:
                raise HTTPException(status_code=400, detail="پلتفرم نامعتبر")
            
            results = await selector.platforms[platform].search_product(q)
            return {"platform": platform, "results": results}
        else:
            # جستجو در همه پلتفرم‌ها
            comparison = await selector.compare_prices(q)
            return comparison
    finally:
        await selector.close_all()

@router.get("/")
def get_products(
    skip: int = 0,
    limit: int = 50,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    دریافت لیست محصولات
    """
    query = db.query(Product)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    products = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "products": products,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }

@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    دریافت جزئیات یک محصول
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="محصول یافت نشد")
    
    # افزایش تعداد بازدید
    product.views += 1
    db.commit()
    
    return product

@router.get("/categories/")
def get_categories(db: Session = Depends(get_db)):
    """
    دریافت لیست دسته‌بندی‌ها
    """
    categories = db.query(Category).filter(Category.parent_id == None).all()
    return {"categories": categories}

@router.post("/sync")
async def sync_products(
    platform: str,
    query: str,
    db: Session = Depends(get_db)
):
    """
    همگام‌سازی محصولات از پلتفرم‌های خارجی
    """
    selector = PlatformSelector()
    
    if platform not in selector.platforms:
        raise HTTPException(status_code=400, detail="پلتفرم نامعتبر")
    
    try:
        results = await selector.platforms[platform].search_product(query)
        
        synced_count = 0
        for item in results:
            # بررسی وجود محصول
            existing = db.query(Product).filter(
                Product.platforms.contains({platform: {"id": item["id"]}})
            ).first()
            
            if not existing:
                # ایجاد محصول جدید
                product = Product(
                    title=item["title"],
                    price=item["price"],
                    main_image=item["image"],
                    platforms={platform: item}
                )
                db.add(product)
                synced_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "synced": synced_count,
            "total_found": len(results)
        }
    finally:
        await selector.close_all()
