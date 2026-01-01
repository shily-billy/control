# app/connectors/manamod.py
import asyncio
import re
from typing import Optional, Dict, List
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from app.connectors.base import BaseConnector, ConnectorResult
from app.common.log import console


class ManamodConnector(BaseConnector):
    """
    کانکتور Manamod برای استخراج آمار و سفارشات
    """
    name = "manamod"
    base_url = "https://manamod.net"
    
    def __init__(self, username: str, password: str, headless: bool = True):
        self.username = username
        self.password = password
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def _init_browser(self):
        """راه‌اندازی Playwright browser"""
        from playwright.async_api import async_playwright
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--lang=fa-IR']
        )
        self.context = await self.browser.new_context(
            locale='fa-IR',
            timezone_id='Asia/Tehran',
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        )
        self.page = await self.context.new_page()
        console.print(f"[green]✓ Browser initialized for {self.name}[/green]")

    async def _close_browser(self):
        """بستن browser"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        console.print(f"[yellow]Browser closed for {self.name}[/yellow]")

    def _extract_number(self, text: str) -> int:
        """استخراج عدد از متن فارسی"""
        if not text:
            return 0
        # حذف کاما و تومان و فاصله
        cleaned = text.replace(',', '').replace('تومان', '').replace(' ', '').strip()
        try:
            return int(cleaned)
        except:
            return 0

    async def login(self) -> ConnectorResult:
        """ورود به پنل همکار Manamod"""
        try:
            if not self.page:
                await self._init_browser()
            
            console.print(f"[cyan]Logging in to {self.name}...[/cyan]")
            
            # رفتن به صفحه لاگین
            await self.page.goto(f"{self.base_url}/login", 
                                wait_until="networkidle", timeout=30000)
            
            # پر کردن فرم لاگین
            await self.page.fill('input[name="email"]', self.username)
            await self.page.fill('input[name="password"]', self.password)
            
            # کلیک روی دکمه ورود
            await self.page.click('button.btn-login')
            
            # صبر برای redirect
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            await asyncio.sleep(2)
            
            # بررسی موفقیت لاگین
            current_url = self.page.url
            if "login" not in current_url.lower():
                console.print(f"[green]✓ Login successful to {self.name}[/green]")
                return ConnectorResult(ok=True, message="Login successful")
            else:
                console.print(f"[red]✗ Login failed to {self.name}[/red]")
                return ConnectorResult(ok=False, message="Login failed - check credentials")
                
        except Exception as e:
            console.print(f"[red]Error during login: {e}[/red]")
            return ConnectorResult(ok=False, message=f"Exception: {str(e)}")

    async def login_test(self) -> ConnectorResult:
        """تست ورود"""
        result = await self.login()
        await self._close_browser()
        return result

    async def get_dashboard_stats(self) -> Dict:
        """دریافت آمار داشبورد"""
        try:
            if not self.page:
                login_result = await self.login()
                if not login_result.ok:
                    return {"error": "Login failed"}
            
            # رفتن به داشبورد
            await self.page.goto(f"{self.base_url}/panel", 
                                wait_until="networkidle", timeout=30000)
            
            await asyncio.sleep(2)
            
            stats = {}
            
            # استخراج 4 کارت آماری اصلی
            stat_cards = await self.page.query_selector_all('.statistic__item')
            
            for card in stat_cards:
                try:
                    # دریافت عنوان و مقدار
                    desc_elem = await card.query_selector('.desc')
                    value_elem = await card.query_selector('h2')
                    
                    if desc_elem and value_elem:
                        desc = await desc_elem.text_content()
                        value = await value_elem.text_content()
                        
                        desc = desc.strip()
                        value_num = self._extract_number(value)
                        
                        # نقشه برداری عناوین
                        if 'سفارشات امروز' in desc:
                            stats['today_orders'] = value_num
                        elif 'موجودی' in desc:
                            stats['balance'] = value_num
                        elif 'پیامک' in desc:
                            stats['sms_received'] = value_num
                        elif 'محصولات' in desc:
                            stats['new_products_week'] = value_num
                            
                except Exception as e:
                    console.print(f"[yellow]Warning parsing stat card: {e}[/yellow]")
                    continue
            
            stats['timestamp'] = datetime.now().isoformat()
            stats['vendor'] = self.name
            
            console.print(f"[green]✓ Dashboard stats retrieved: {len(stats)} metrics[/green]")
            return stats
            
        except Exception as e:
            console.print(f"[red]Error getting dashboard stats: {e}[/red]")
            return {"error": str(e)}

    async def get_orders(self, status: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        دریافت لیست سفارشات
        
        status: None (all), "14" (pending), "19" (confirmed), "8" (cancelled)
        """
        try:
            if not self.page:
                login_result = await self.login()
                if not login_result.ok:
                    return []
            
            # ساخت URL
            url = f"{self.base_url}/orders/list"
            if status:
                url += f"?status={status}"
            
            # رفتن به صفحه سفارشات
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            
            orders = []
            
            # بررسی وجود جدول سفارشات
            no_orders = await self.page.query_selector('text=سفارشی پیدا نشد')
            if no_orders:
                console.print(f"[yellow]No orders found for status={status}[/yellow]")
                return []
            
            # استخراج ردیف‌های جدول (باید ساختار جدول را بررسی کنیم)
            # فعلاً placeholder
            rows = await self.page.query_selector_all('table tbody tr')
            
            for idx, row in enumerate(rows[:limit]):
                try:
                    order = {}
                    
                    # TODO: سلکتورهای دقیق بعد از دیدن جدول واقعی
                    cells = await row.query_selector_all('td')
                    
                    if len(cells) >= 5:
                        # فرض: شناسه، محصول، مبلغ، تاریخ، وضعیت
                        order['order_id'] = await cells[0].text_content()
                        order['product'] = await cells[1].text_content()
                        price_text = await cells[2].text_content()
                        order['price'] = self._extract_number(price_text)
                        order['date'] = await cells[3].text_content()
                        order['status'] = await cells[4].text_content()
                        
                        orders.append(order)
                    
                except Exception as e:
                    console.print(f"[yellow]Warning parsing order row {idx}: {e}[/yellow]")
                    continue
            
            console.print(f"[green]✓ Retrieved {len(orders)} orders from {self.name}[/green]")
            return orders
            
        except Exception as e:
            console.print(f"[red]Error getting orders: {e}[/red]")
            return []

    async def get_orders_by_status(self) -> Dict[str, List[Dict]]:
        """دریافت سفارشات تفکیک شده بر اساس وضعیت"""
        try:
            console.print(f"[cyan]Fetching orders by status...[/cyan]")
            
            result = {
                "all": await self.get_orders(status=None, limit=50),
                "pending": await self.get_orders(status="14", limit=50),
                "confirmed": await self.get_orders(status="19", limit=50),
                "cancelled": await self.get_orders(status="8", limit=50)
            }
            
            total = sum(len(orders) for orders in result.values())
            console.print(f"[green]✓ Total orders fetched: {total}[/green]")
            
            return result
            
        except Exception as e:
            console.print(f"[red]Error getting orders by status: {e}[/red]")
            return {}

    async def sync_all_data(self) -> Dict:
        """همگام‌سازی کامل تمام داده‌ها"""
        try:
            console.print(f"[cyan]Starting full sync for {self.name}...[/cyan]")
            
            login_result = await self.login()
            if not login_result.ok:
                return {
                    "success": False,
                    "error": "Login failed",
                    "vendor": self.name
                }
            
            # دریافت تمام داده‌ها
            stats = await self.get_dashboard_stats()
            orders_all = await self.get_orders(status=None, limit=100)
            
            result = {
                "success": True,
                "vendor": self.name,
                "timestamp": datetime.now().isoformat(),
                "stats": stats,
                "orders": orders_all,
                "orders_count": len(orders_all),
                "summary": {
                    "today_orders": stats.get('today_orders', 0),
                    "balance": stats.get('balance', 0),
                    "sms_received": stats.get('sms_received', 0),
                    "new_products": stats.get('new_products_week', 0)
                }
            }
            
            console.print(f"[green]✓ Full sync completed for {self.name}[/green]")
            console.print(f"[cyan]  → {len(orders_all)} orders, {stats.get('balance', 0):,} تومان balance[/cyan]")
            
            return result
            
        except Exception as e:
            console.print(f"[red]Error during full sync: {e}[/red]")
            return {
                "success": False,
                "error": str(e),
                "vendor": self.name
            }
        finally:
            await self._close_browser()


# تست مستقیم
async def test_manamod():
    """تابع تست برای Manamod connector"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    username = os.getenv("MANAMOD_USERNAME", "")
    password = os.getenv("MANAMOD_PASSWORD", "")
    
    if not username or not password:
        console.print("[red]❌ Please set MANAMOD_USERNAME and MANAMOD_PASSWORD in .env[/red]")
        return
    
    connector = ManamodConnector(username, password, headless=False)
    
    # تست sync کامل
    result = await connector.sync_all_data()
    
    console.print("\n[cyan]========== SYNC RESULT ==========[/cyan]")
    console.print(result)


if __name__ == "__main__":
    asyncio.run(test_manamod())
