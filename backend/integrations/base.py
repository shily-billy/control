from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import httpx
import asyncio
from bs4 import BeautifulSoup

class BasePlatform(ABC):
    """
    کلاس پایه برای تمام پلتفرم‌ها
    """
    
    def __init__(self, name: str, base_url: str, commission_rate: float):
        self.name = name
        self.base_url = base_url
        self.commission_rate = commission_rate
        self.session = None
    
    async def init_session(self):
        if not self.session:
            self.session = httpx.AsyncClient(timeout=30.0)
    
    async def close_session(self):
        if self.session:
            await self.session.aclose()
    
    @abstractmethod
    async def search_product(self, query: str) -> List[Dict]:
        """جستجوی محصول"""
        pass
    
    @abstractmethod
    async def get_product_details(self, product_id: str) -> Optional[Dict]:
        """دریافت جزئیات محصول"""
        pass
    
    @abstractmethod
    async def get_price(self, product_id: str) -> Optional[float]:
        """دریافت قیمت محصول"""
        pass
    
    def calculate_commission(self, price: float) -> float:
        """محاسبه کمیسیون"""
        return price * self.commission_rate
    
    def generate_affiliate_link(self, product_url: str, affiliate_id: str) -> str:
        """ساخت لینک افیلیت"""
        return f"{product_url}?ref={affiliate_id}"
