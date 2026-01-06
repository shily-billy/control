from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from models.product import Product
from services.platform_selector import PlatformSelector
from pydantic import BaseModel

router = APIRouter()

class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    base_price: float
    category: Optional[str] = None
    main_image: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    title: str
    final_price: float
    main_image: Optional[str]
    category: Optional[str]
    in_stock: bool
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = Query(50, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    دریافت لیست محصولات
    """
    query = db.query(Product).filter(Product.is_active == True)
    
    if category:
        query = query.filter(Product.category == category)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    دریافت جزئیات یک محصول
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="محصول یافت نشد")
    return product

@router.get("/{product_id}/best-platform")
async def get_best_platform(product_id: int, db: Session = Depends(get_db)):
    """
    دریافت بهترین پلتفرم برای فروش این محصول
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="محصول یافت نشد")
    
    product_data = {
        "price": product.final_price,
        "category": product.category
    }
    
    best_platform = PlatformSelector.select_best_platform(product_data)
    all_platforms = PlatformSelector.get_all_platforms_comparison(product_data)
    
    return {
        "product": {
            "id": product.id,
            "title": product.title,
            "price": product.final_price
        },
        "best_platform": best_platform,
        "all_platforms": all_platforms
    }

@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    ایجاد محصول جدید
    """
    from slugify import slugify
    
    db_product = Product(
        title=product.title,
        slug=slugify(product.title),
        description=product.description,
        base_price=product.base_price,
        final_price=product.base_price,
        category=product.category,
        main_image=product.main_image
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product