from fastapi import APIRouter, HTTPException
from services.platform_selector import PlatformSelector

router = APIRouter()

@router.get("/")
def get_platforms():
    """
    دریافت لیست پلتفرم‌های موجود
    """
    return {
        "platforms": [
            {"name": "digikala", "title": "دیجی‌کالا", "commission": "9-20%"},
            {"name": "mihanstore", "title": "میهن استور", "commission": "30-50%"},
            {"name": "torob", "title": "ترب", "commission": "10%"},
            {"name": "bamilo", "title": "بامیلو", "commission": "25%"},
            {"name": "divar", "title": "دیوار", "type": "marketplace"},
            {"name": "sheypoor", "title": "شیپور", "type": "marketplace"},
        ]
    }

@router.get("/commissions")
def get_commission_rates():
    """
    دریافت نرخ کمیسیون پلتفرم‌ها
    """
    selector = PlatformSelector()
    
    rates = {}
    for name, platform in selector.platforms.items():
        rates[name] = {
            "name": platform.name,
            "commission_rate": platform.commission_rate,
            "commission_percent": f"{platform.commission_rate * 100}%"
        }
    
    return rates
