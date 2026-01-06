from typing import List, Dict, Optional
import httpx
from .base import BasePlatform

class TorobIntegration(BasePlatform):
    """
    اتصال به ترب (مقایسه قیمت)
    """
    
    def __init__(self, api_key: str = "", commission_rate: float = 0.10):
        super().__init__("torob", "https://torob.com", commission_rate)
        self.api_key = api_key
        self.api_base = "https://api.torob.com/v4"
    
    async def search_product(self, query: str) -> List[Dict]:
        """جستجو در ترب"""
        await self.init_session()
        
        url = f"{self.api_base}/search/"
        params = {"q": query}
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        
        try:
            response = await self.session.get(url, params=params, headers=headers)
            data = response.json()
            
            products = []
            if "results" in data:
                for item in data["results"]:
                    products.append({
                        "id": str(item.get("web_client_absolute_url", "").split("/")[-1]),
                        "title": item.get("name1"),
                        "price": item.get("price", {}).get("min", 0) / 10,
                        "image": item.get("image_url"),
                        "url": f"{self.base_url}{item.get('web_client_absolute_url')}",
                        "platform": self.name
                    })
            
            return products
        except Exception as e:
            print(f"Torob search error: {e}")
            return []
    
    async def get_product_details(self, product_id: str) -> Optional[Dict]:
        await self.init_session()
        
        url = f"{self.api_base}/product/{product_id}/"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        
        try:
            response = await self.session.get(url, headers=headers)
            data = response.json()
            
            return {
                "id": product_id,
                "title": data.get("name1"),
                "description": data.get("description"),
                "price": data.get("price", {}).get("min", 0) / 10,
                "images": [data.get("image_url")],
                "platform": self.name
            }
        except Exception as e:
            print(f"Torob product details error: {e}")
            return None
    
    async def get_price(self, product_id: str) -> Optional[float]:
        details = await self.get_product_details(product_id)
        return details.get("price") if details else None
