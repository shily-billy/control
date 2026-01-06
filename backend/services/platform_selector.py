from typing import List, Dict, Optional
from integrations.digikala import DigikalaIntegration
from integrations.mihanstore import MihanstoreIntegration
from integrations.torob import TorobIntegration
from core.config import settings

class PlatformSelector:
    """
    سیستم هوشمند انتخاب پلتفرم با بیشترین سود
    """
    
    def __init__(self):
        self.platforms = {
            "digikala": DigikalaIntegration(
                affiliate_id=settings.DIGIKALA_AFFILIATE_ID,
                commission_rate=0.12
            ),
            "mihanstore": MihanstoreIntegration(
                partner_id=settings.MIHANSTORE_PARTNER_ID,
                commission_rate=0.40
            ),
            "torob": TorobIntegration(
                api_key=settings.TOROB_API_KEY,
                commission_rate=0.10
            )
        }
    
    async def search_all_platforms(self, query: str) -> Dict[str, List[Dict]]:
        """جستجو در تمام پلتفرم‌ها"""
        results = {}
        
        for platform_name, platform in self.platforms.items():
            try:
                products = await platform.search_product(query)
                results[platform_name] = products
            except Exception as e:
                print(f"Error searching {platform_name}: {e}")
                results[platform_name] = []
        
        return results
    
    def select_best_platform(self, product_title: str, platforms_data: Dict[str, List[Dict]]) -> Optional[Dict]:
        """
        انتخاب بهترین پلتفرم بر اساس:
        1. بیشترین کمیسیون
        2. موجودی محصول
        3. قیمت مناسب
        """
        best_option = None
        max_profit = 0
        
        for platform_name, products in platforms_data.items():
            if not products:
                continue
            
            platform = self.platforms[platform_name]
            
            # پیدا کردن محصول مشابه
            for product in products:
                if product.get("in_stock", True):
                    price = product.get("price", 0)
                    commission = platform.calculate_commission(price)
                    
                    # محاسبه سود خالص
                    profit = commission
                    
                    if profit > max_profit:
                        max_profit = profit
                        best_option = {
                            "platform": platform_name,
                            "product": product,
                            "commission": commission,
                            "commission_rate": platform.commission_rate,
                            "profit": profit
                        }
        
        return best_option
    
    async def compare_prices(self, product_title: str) -> Dict:
        """
        مقایسه قیمت در تمام پلتفرم‌ها
        """
        all_results = await self.search_all_platforms(product_title)
        best = self.select_best_platform(product_title, all_results)
        
        return {
            "query": product_title,
            "all_platforms": all_results,
            "recommended": best,
            "total_platforms_checked": len(self.platforms),
            "platforms_with_results": sum(1 for r in all_results.values() if r)
        }
    
    async def close_all(self):
        """بستن تمام سشن‌ها"""
        for platform in self.platforms.values():
            await platform.close_session()
