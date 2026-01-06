from typing import List, Dict, Optional
import httpx
from bs4 import BeautifulSoup
import re
from .base import BasePlatform

class MihanstoreIntegration(BasePlatform):
    """
    اتصال به میهن استور (کمیسیون بالا برای پوشاک)
    """
    
    def __init__(self, partner_id: str = "", commission_rate: float = 0.40):
        super().__init__("mihanstore", "https://mihanstore.net", commission_rate)
        self.partner_id = partner_id
    
    async def search_product(self, query: str) -> List[Dict]:
        """جستجو در میهن استور"""
        await self.init_session()
        
        url = f"{self.base_url}/search"
        params = {"q": query}
        
        try:
            response = await self.session.get(url, params=params)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            products = []
            product_items = soup.select('.product-item')
            
            for item in product_items:
                try:
                    title = item.select_one('.product-title').text.strip()
                    price_text = item.select_one('.product-price').text.strip()
                    price = float(re.sub(r'[^0-9]', '', price_text)) / 1000  # تبدیل به هزار تومان
                    image = item.select_one('img')['src']
                    link = item.select_one('a')['href']
                    product_id = link.split('/')[-1]
                    
                    products.append({
                        "id": product_id,
                        "title": title,
                        "price": price,
                        "image": image if image.startswith('http') else f"{self.base_url}{image}",
                        "url": f"{self.base_url}{link}" if not link.startswith('http') else link,
                        "platform": self.name,
                        "commission": self.calculate_commission(price)
                    })
                except Exception as e:
                    continue
            
            return products
        except Exception as e:
            print(f"Mihanstore search error: {e}")
            return []
    
    async def get_product_details(self, product_id: str) -> Optional[Dict]:
        """دریافت جزئیات محصول"""
        await self.init_session()
        
        url = f"{self.base_url}/product/{product_id}"
        
        try:
            response = await self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.select_one('h1.product-title').text.strip()
            description = soup.select_one('.product-description').text.strip()
            price_text = soup.select_one('.product-price').text.strip()
            price = float(re.sub(r'[^0-9]', '', price_text)) / 1000
            
            images = [img['src'] for img in soup.select('.product-gallery img')]
            
            return {
                "id": product_id,
                "title": title,
                "description": description,
                "price": price,
                "images": images,
                "platform": self.name,
                "commission": self.calculate_commission(price)
            }
        except Exception as e:
            print(f"Mihanstore product details error: {e}")
            return None
    
    async def get_price(self, product_id: str) -> Optional[float]:
        details = await self.get_product_details(product_id)
        return details.get("price") if details else None
    
    def generate_affiliate_link(self, product_id: str) -> str:
        base_url = f"{self.base_url}/product/{product_id}"
        if self.partner_id:
            return f"{base_url}?ref={self.partner_id}"
        return base_url
