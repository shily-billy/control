import asyncio
import re
from typing import Optional, Dict, List
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from app.connectors.base import BaseConnector, ConnectorResult
from app.common.log import console


class MihanstoreConnector(BaseConnector):
    """
    کانکتور میهن استور برای استخراج آمار و سفارشات
    """
    name = "mihanstore"
    base_url = "https://mihanstore.net/partner"
    
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
        """ورود به پنل همکار میهن استور"""
        try:
            if not self.page:
                await self._init_browser()
            
            console.print(f"[cyan]Logging in to {self.name}...[/cyan]")
            
            # رفتن به صفحه لاگین
            await self.page.goto(f"{self.base_url}/index.php?act=logins", 
                                wait_until="networkidle", timeout=30000)
            
            # پر کردن فرم لاگین
            await self.page.fill('input[name="username"]', self.username)
            await self.page.fill('input[name="password"]', self.password)
            
            # ⚠️ CAPTCHA: باید دستی حل بشه
            console.print("[yellow]⚠️  Please solve CAPTCHA manually (you have 30 seconds)...[/yellow]")
            
            # صبر برای حل دستی کپچا
            if not self.headless:
                await asyncio.sleep(30)
            else:
                console.print("[red]❌ Cannot solve CAPTCHA in headless mode![/red]")
                return ConnectorResult(ok=False, message="CAPTCHA required - use headless=False")
            
            # کلیک روی دکمه ورود
            await self.page.click('input[name="submit"][type="submit"]')
            
            # صبر برای redirect
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            await asyncio.sleep(2)
            
            # بررسی موفقیت لاگین
            current_url = self.page.url
            if "logins" not in current_url.lower():
                console.print(f"[green]✓ Login successful to {self.name}[/green]")
                return ConnectorResult(ok=True, message="Login successful")
            else:
                console.print(f"[red]✗ Login failed to {self.name}[/red]")
                return ConnectorResult(ok=False, message="Login failed - check credentials or CAPTCHA")
                
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
            await self.page.goto(f"{self.base_url}/index.php", 
                                wait_until="networkidle", timeout=30000)
            
            await asyncio.sleep(2)
            
            stats = {}
            
            # استخراج تمام کارت‌های آمار
            cards = await self.page.query_selector_all('.card-stats')
            
            for card in cards:
                try:
                    title_elem = await card.query_selector('h5.card-title')
                    value_elem = await card.query_selector('span.h2.font-weight-bold')
                    
                    if title_elem and value_elem:
                        title = await title_elem.text_content()
                        value = await value_elem.text_content()
                        
                        title = title.strip().replace(':', '').strip()
                        value_num = self._extract_number(value)
                        
                        # نقشه برداری عناوین
                        if 'سفارشات کل' in title:
                            stats['total_orders'] = value_num
                        elif 'درآمد کل' in title:
                            stats['total_revenue'] = value_num
                        elif 'تعیین تکلیف شده' in title:
                            stats['completed_orders'] = value_num
                        elif 'در حال بررسی' in title:
                            stats['pending_orders'] = value_num
                        elif 'سفارشات دیروز' in title:
                            stats['yesterday_orders'] = value_num
                        elif 'سفارشات امروز' in title:
                            stats['today_orders'] = value_num
                        elif 'درآمد از بازاریابی' in title:
                            stats['referral_revenue'] = value_num
                        elif 'درآمد پرداخت شده' in title:
                            stats['paid_revenue'] = value_num
                        elif 'کسر بابت برگشتی' in title:
                            stats['return_deduction'] = value_num
                        elif 'درآمد قابل برداشت' in title:
                            stats['withdrawable_revenue'] = value_num
                except Exception as e:
                    console.print(f"[yellow]Warning parsing card: {e}[/yellow]")
                    continue
            
            stats['timestamp'] = datetime.now().isoformat()
            stats['vendor'] = self.name
            
            console.print(f"[green]✓ Dashboard stats retrieved: {len(stats)} metrics[/green]")
            return stats
            
        except Exception as e:
            console.print(f"[red]Error getting dashboard stats: {e}[/red]")
            return {"error": str(e)}

    async def get_orders(self, limit: int = 50) -> List[Dict]:
        """دریافت لیست سفارشات"""
        try:
            if not self.page:
                login_result = await self.login()
                if not login_result.ok:
                    return []
            
            # رفتن به صفحه سفارشات
            await self.page.goto(f"{self.base_url}/index.php?act=orders", 
                                wait_until="networkidle", timeout=30000)
            
            await asyncio.sleep(2)
            
            orders = []
            
            # استخراج ردیف‌های جدول
            rows = await self.page.query_selector_all('table#myTable tbody tr')
            
            for idx, row in enumerate(rows[:limit]):
                try:
                    order = {}
                    
                    # شماره سفارش
                    order_id_elem = await row.query_selector('td.id')
                    if order_id_elem:
                        order['order_id'] = (await order_id_elem.text_content()).strip()
                    
                    # نام محصول
                    product_elem = await row.query_selector('span.name.mb-0')
                    if product_elem:
                        order['product'] = (await product_elem.text_content()).strip()
                    
                    # سهم همکار
                    budget_elem = await row.query_selector('td.budget')
                    if budget_elem:
                        budget_text = await budget_elem.text_content()
                        order['commission'] = budget_text.strip()
                        order['commission_amount'] = self._extract_number(budget_text)
                    
                    # تاریخ
                    date_elems = await row.query_selector_all('td span.status')
                    if len(date_elems) >= 1:
                        order['date'] = (await date_elems[0].text_content()).strip()
                    
                    # شناسه پستی
                    if len(date_elems) >= 2:
                        tracking = (await date_elems[1].text_content()).strip()
                        order['tracking_code'] = tracking if tracking else None
                    
                    # وضعیت
                    if len(date_elems) >= 3:
                        order['status'] = (await date_elems[2].text_content()).strip()
                    
                    orders.append(order)
                    
                except Exception as e:
                    console.print(f"[yellow]Warning parsing order row {idx}: {e}[/yellow]")
                    continue
            
            console.print(f"[green]✓ Retrieved {len(orders)} orders from {self.name}[/green]")
            return orders
            
        except Exception as e:
            console.print(f"[red]Error getting orders: {e}[/red]")
            return []

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
            orders = await self.get_orders(limit=100)
            
            result = {
                "success": True,
                "vendor": self.name,
                "timestamp": datetime.now().isoformat(),
                "stats": stats,
                "orders": orders,
                "orders_count": len(orders),
                "summary": {
                    "total_orders": stats.get('total_orders', 0),
                    "total_revenue": stats.get('total_revenue', 0),
                    "withdrawable": stats.get('withdrawable_revenue', 0)
                }
            }
            
            console.print(f"[green]✓ Full sync completed for {self.name}[/green]")
            console.print(f"[cyan]  → {len(orders)} orders, {stats.get('total_revenue', 0):,} تومان revenue[/cyan]")
            
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
async def test_mihanstore():
    """تابع تست برای Mihanstore connector"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    username = os.getenv("MIHANSTORE_USERNAME", "")
    password = os.getenv("MIHANSTORE_PASSWORD", "")
    
    if not username or not password:
        console.print("[red]❌ Please set MIHANSTORE_USERNAME and MIHANSTORE_PASSWORD in .env[/red]")
        return
    
    connector = MihanstoreConnector(username, password, headless=False)
    
    # تست sync کامل
    result = await connector.sync_all_data()
    
    console.print("\n[cyan]========== SYNC RESULT ==========[/cyan]")
    console.print(result)


if __name__ == "__main__":
    asyncio.run(test_mihanstore())
