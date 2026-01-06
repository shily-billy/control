from fastapi import APIRouter
from services.platform_selector import PlatformSelector

router = APIRouter()

@router.get("/list")
async def get_platforms():
    """
    دریافت لیست تمام پلتفرم‌های پشتیبانی شده
    """
    return {
        "platforms": PlatformSelector.PLATFORMS
    }

@router.get("/compare")
async def compare_platforms(price: float, category: str = None):
    """
    مقایسه پلتفرم‌ها برای یک محصول
    """
    product_data = {
        "price": price,
        "category": category
    }
    
    comparison = PlatformSelector.get_all_platforms_comparison(product_data)
    return {"comparison": comparison}