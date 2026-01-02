# app/orchestrator.py
"""
Orchestrator اصلی برای مدیریت همگام‌سازی تمام فروشگاه‌ها
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from app.connectors.mihanstore import MihanstoreConnector
from app.connectors.manamod import ManamodConnector
from app.connectors.memarket import MemarketConnector
from app.common.log import console
import os
from dotenv import load_dotenv


class VendorOrchestrator:
    """
    هماهنگ‌کننده اصلی برای مدیریت sync تمام فروشگاه‌ها
    """
    
    def __init__(self, headless: bool = True):
        """
        Args:
            headless: اجرای browser بدون نمایش UI
        """
        self.headless = headless
        self.vendors = {}
        self.results = {}
        load_dotenv()
        
    def _init_connectors(self):
        """راه‌اندازی تمام کانکتورهای فعال"""
        
        # Mihanstore
        mihanstore_user = os.getenv("MIHANSTORE_USERNAME")
        mihanstore_pass = os.getenv("MIHANSTORE_PASSWORD")
        if mihanstore_user and mihanstore_pass:
            self.vendors['mihanstore'] = MihanstoreConnector(
                username=mihanstore_user,
                password=mihanstore_pass,
                headless=self.headless
            )
            console.print("[cyan]✓ Mihanstore connector loaded[/cyan]")
        
        # Manamod
        manamod_user = os.getenv("MANAMOD_USERNAME")
        manamod_pass = os.getenv("MANAMOD_PASSWORD")
        if manamod_user and manamod_pass:
            self.vendors['manamod'] = ManamodConnector(
                username=manamod_user,
                password=manamod_pass,
                headless=self.headless
            )
            console.print("[cyan]✓ Manamod connector loaded[/cyan]")
        
        # Memarket (فعلاً غیرفعال)
        # memarket_user = os.getenv("MEMARKET_USERNAME")
        # memarket_pass = os.getenv("MEMARKET_PASSWORD")
        # if memarket_user and memarket_pass:
        #     self.vendors['memarket'] = MemarketConnector(...)
        
        if not self.vendors:
            console.print("[red]⚠ No vendors configured! Check .env file[/red]")
        
        return len(self.vendors)
    
    async def sync_single_vendor(self, vendor_name: str) -> Dict:
        """
        همگام‌سازی یک فروشگاه
        
        Args:
            vendor_name: نام فروشگاه (mihanstore, manamod, memarket)
            
        Returns:
            Dict با نتایج sync
        """
        if vendor_name not in self.vendors:
            return {
                "success": False,
                "vendor": vendor_name,
                "error": "Vendor not found or not configured"
            }
        
        connector = self.vendors[vendor_name]
        
        try:
            console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
            console.print(f"[bold cyan]🔄 Syncing: {vendor_name.upper()}[/bold cyan]")
            console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
            
            # اجرای sync
            result = await connector.sync_all_data()
            
            # ذخیره نتیجه
            self.results[vendor_name] = result
            
            if result.get("success"):
                console.print(f"[green]✓ {vendor_name} sync completed successfully[/green]")
            else:
                console.print(f"[red]✗ {vendor_name} sync failed: {result.get('error')}[/red]")
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "vendor": vendor_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results[vendor_name] = error_result
            console.print(f"[red]✗ Exception in {vendor_name}: {e}[/red]")
            return error_result
    
    async def sync_all_vendors(self) -> Dict:
        """
        همگام‌سازی همزمان تمام فروشگاه‌ها
        
        Returns:
            Dict با نتایج کلی sync
        """
        console.print("\n[bold green]🚀 Starting Multi-Vendor Sync[/bold green]\n")
        
        # راه‌اندازی کانکتورها
        vendor_count = self._init_connectors()
        if vendor_count == 0:
            return {
                "success": False,
                "error": "No vendors configured",
                "timestamp": datetime.now().isoformat()
            }
        
        # ساخت taskهای async برای sync همزمان
        tasks = []
        for vendor_name in self.vendors.keys():
            task = self.sync_single_vendor(vendor_name)
            tasks.append(task)
        
        # اجرای همزمان تمام taskها
        start_time = datetime.now()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # جمع‌آوری نتایج
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        failed = len(results) - successful
        
        summary = {
            "success": failed == 0,
            "timestamp": end_time.isoformat(),
            "duration_seconds": duration,
            "total_vendors": len(results),
            "successful": successful,
            "failed": failed,
            "vendors": self.results
        }
        
        # نمایش خلاصه
        console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold cyan]📊 SYNC SUMMARY[/bold cyan]")
        console.print(f"[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"Total Vendors: {summary['total_vendors']}")
        console.print(f"[green]✓ Successful: {summary['successful']}[/green]")
        console.print(f"[red]✗ Failed: {summary['failed']}[/red]")
        console.print(f"Duration: {summary['duration_seconds']:.2f}s")
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
        
        return summary
    
    def get_unified_stats(self) -> Dict:
        """
        دریافت آمار یکپارچه از تمام فروشگاه‌ها
        
        Returns:
            Dict با آمار ترکیبی
        """
        if not self.results:
            return {
                "error": "No sync results available. Run sync_all_vendors() first."
            }
        
        unified = {
            "timestamp": datetime.now().isoformat(),
            "total_orders": 0,
            "total_revenue": 0,
            "total_balance": 0,
            "vendors_detail": {}
        }
        
        for vendor_name, result in self.results.items():
            if not result.get("success"):
                continue
            
            stats = result.get("stats", {})
            summary = result.get("summary", {})
            orders = result.get("orders", [])
            
            # جمع آمار کلی
            unified["total_orders"] += len(orders)
            
            # درآمد (از Mihanstore)
            if vendor_name == "mihanstore":
                total_sales = stats.get("total_sales", 0)
                if isinstance(total_sales, str):
                    # پارس کردن "1,234,567 تومان"
                    total_sales = int(total_sales.replace(',', '').replace('تومان', '').strip())
                unified["total_revenue"] += total_sales
            
            # موجودی (از Manamod)
            if vendor_name == "manamod":
                balance = summary.get("balance", 0)
                unified["total_balance"] += balance
            
            # جزئیات هر vendor
            unified["vendors_detail"][vendor_name] = {
                "orders_count": len(orders),
                "stats": stats,
                "summary": summary
            }
        
        return unified
    
    async def test_all_logins(self) -> Dict:
        """
        تست login تمام فروشگاه‌ها
        
        Returns:
            Dict با نتایج تست login
        """
        console.print("\n[bold yellow]🔐 Testing All Logins[/bold yellow]\n")
        
        self._init_connectors()
        
        results = {}
        for vendor_name, connector in self.vendors.items():
            try:
                console.print(f"Testing {vendor_name}...", end=" ")
                result = await connector.login_test()
                results[vendor_name] = {
                    "success": result.ok,
                    "message": result.message
                }
                
                if result.ok:
                    console.print("[green]✓ OK[/green]")
                else:
                    console.print(f"[red]✗ FAILED: {result.message}[/red]")
                    
            except Exception as e:
                results[vendor_name] = {
                    "success": False,
                    "message": str(e)
                }
                console.print(f"[red]✗ ERROR: {e}[/red]")
        
        return results


# ==================== CLI Commands ====================

async def sync_all():
    """کمند: همگام‌سازی همه فروشگاه‌ها"""
    orchestrator = VendorOrchestrator(headless=True)
    summary = await orchestrator.sync_all_vendors()
    
    # نمایش آمار یکپارچه
    unified = orchestrator.get_unified_stats()
    
    console.print("\n[bold green]📈 UNIFIED STATISTICS[/bold green]")
    console.print(f"Total Orders: {unified['total_orders']}")
    console.print(f"Total Revenue: {unified['total_revenue']:,} تومان")
    console.print(f"Total Balance: {unified['total_balance']:,} تومان")
    
    return summary


async def sync_vendor(vendor_name: str):
    """کمند: همگام‌سازی یک فروشگاه"""
    orchestrator = VendorOrchestrator(headless=True)
    orchestrator._init_connectors()
    
    result = await orchestrator.sync_single_vendor(vendor_name)
    return result


async def test_logins():
    """کمند: تست login همه فروشگاه‌ها"""
    orchestrator = VendorOrchestrator(headless=False)
    results = await orchestrator.test_all_logins()
    return results


# ==================== Main ====================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m app.orchestrator sync-all          # Sync all vendors")
        print("  python -m app.orchestrator sync <vendor>     # Sync specific vendor")
        print("  python -m app.orchestrator test-logins       # Test all logins")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "sync-all":
        asyncio.run(sync_all())
    elif command == "sync" and len(sys.argv) >= 3:
        vendor = sys.argv[2]
        asyncio.run(sync_vendor(vendor))
    elif command == "test-logins":
        asyncio.run(test_logins())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
