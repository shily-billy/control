from typing import List, Dict, Optional
import httpx
from bs4 import BeautifulSoup
import json
from .base import BasePlatform

class DigikalaIntegration(BasePlatform):
    """
    اتصال به دیجی‌کالا
    """
    
    def __init__(self, affiliate_id: str = "", commission_rate: float = 0.12):
        super().__init__("digikala", "https://www.digikala.com", commission_rate)
        self.affiliate_id = affiliate_id
        self.api_base = "https://api.digikala.com/v1"
    
    async def search_product(self, query: str, page: int = 1) -> List[Dict]:
        """جستجو در دیجی‌کالا"""
        await self.init_session()
        
        url = f"{self.api_base}/search/"
        params = {
            "q": query,
            "page": page
        }
        
        try:
            response = await self.session.get(url, params=params)
            data = response.json()
            
            products = []
            if "data" in data and "products" in data["data"]:
                for item in data["data"]["products"]:
                    products.append({
                        "id": str(item.get("id")),
                        "title": item.get("title_fa"),
                        "price": item.get("default_variant", {}).get("price", {}).get("selling_price", 0) / 10,
                        "image": item.get("images", {}).get("main", {}).get("url", [""])[0],
                        "url": f"{self.base_url}/product/dkp-{item.get('id')}",
                        "platform": self.name,
                        "in_stock": item.get("default_variant", {}).get("is_active", False)
                    })
            
            return products
        except Exception as e:
            print(f"Digikala search error: {e}")
            return []
    
    async def get_product_details(self, product_id: str) -> Optional[Dict]:
        """دریافت جزئیات محصول"""
        await self.init_session()
        
        url = f"{self.api_base}/product/{product_id}/"
        
        try:
            response = await self.session.get(url)
            data = response.json()
            
            if "data" in data and "product" in data["data"]:
                product = data["data"]["product"]
                return {
                    "id": str(product.get("id")),
                    "title": product.get("title_fa"),
                    "description": product.get("review", {}).get("description"),
                    "price": product.get("default_variant", {}).get("price", {}).get("selling_price", 0) / 10,
                    "original_price": product.get("default_variant", {}).get("price", {}).get("rrp_price", 0) / 10,
                    "images": [img.get("url", [""])[0] for img in product.get("images", {}).get("list", [])],
                    "category": product.get("category", {}).get("title_fa"),
                    "brand": product.get("brand", {}).get("title_fa"),
                    "rating": product.get("rating", {}).get("rate", 0),
                    "platform": self.name
                }
        except Exception as e:
            print(f"Digikala product details error: {e}")
            return None
    
    async def get_price(self, product_id: str) -> Optional[float]:
        """دریافت قیمت فعلی"""
        details = await self.get_product_details(product_id)
        return details.get("price") if details else None
    
    def generate_affiliate_link(self, product_id: str) -> str:
        """ساخت لینک افیلیت"""
        base_url = f"{self.base_url}/product/dkp-{product_id}"
        if self.affiliate_id:
            return f"{base_url}/?promo={self.affiliate_id}"
        return base_url
