from typing import Dict, List, Optional
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class PlatformSelector:
    """
    هوش مصنوعی انتخاب بهترین پلتفرم برای هر محصول
    """
    
    PLATFORMS = {
        "digikala": {
            "name": "دیجی‌کالا",
            "commission_rate": 0.12,
            "shipping_cost": 0,
            "reliability_score": 9.5,
            "categories": ["electronics", "fashion", "home", "beauty"]
        },
        "mihanstore": {
            "name": "میهن استور",
            "commission_rate": 0.40,
            "shipping_cost": 0,
            "reliability_score": 8.8,
            "categories": ["fashion", "shoes", "bags"]
        },
        "bamilo": {
            "name": "بامیلو",
            "commission_rate": 0.25,
            "shipping_cost": 0,
            "reliability_score": 8.5,
            "categories": ["fashion", "beauty", "accessories"]
        },
        "torob": {
            "name": "ترب",
            "commission_rate": 0.10,
            "shipping_cost": 0,
            "reliability_score": 9.0,
            "categories": ["electronics", "fashion", "home"]
        },
        "technolife": {
            "name": "تکنولایف",
            "commission_rate": 0.12,
            "shipping_cost": 0,
            "reliability_score": 8.7,
            "categories": ["electronics", "mobile", "laptop"]
        }
    }
    
    @classmethod
    def select_best_platform(cls, product_data: Dict) -> Dict:
        """
        انتخاب بهترین پلتفرم بر اساس محصول
        
        Args:
            product_data: اطلاعات محصول شامل قیمت، دسته‌بندی و...
        
        Returns:
            بهترین پلتفرم با جزئیات
        """
        price = product_data.get("price", 0)
        category = product_data.get("category", "")
        
        best_platform = None
        best_score = -1
        
        for platform_key, platform in cls.PLATFORMS.items():
            # Check if platform supports this category
            if category and category not in platform["categories"]:
                continue
            
            # Calculate profit score
            commission = price * platform["commission_rate"]
            shipping = platform["shipping_cost"]
            reliability = platform["reliability_score"]
            
            # Score formula
            score = commission - shipping + (reliability * 10)
            
            if score > best_score:
                best_score = score
                best_platform = {
                    "platform": platform_key,
                    "name": platform["name"],
                    "commission": commission,
                    "commission_rate": platform["commission_rate"],
                    "profit": commission - shipping,
                    "score": score
                }
        
        logger.info(f"Selected platform: {best_platform['name']} with score: {best_score}")
        return best_platform
    
    @classmethod
    def get_all_platforms_comparison(cls, product_data: Dict) -> List[Dict]:
        """
        مقایسه تمام پلتفرم‌ها برای یک محصول
        """
        price = product_data.get("price", 0)
        results = []
        
        for platform_key, platform in cls.PLATFORMS.items():
            commission = price * platform["commission_rate"]
            results.append({
                "platform": platform_key,
                "name": platform["name"],
                "commission": commission,
                "commission_rate": platform["commission_rate"],
                "reliability_score": platform["reliability_score"]
            })
        
        # Sort by commission (descending)
        results.sort(key=lambda x: x["commission"], reverse=True)
        return results