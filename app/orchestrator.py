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

# Database imports
from app.database.session import get_db
from app.database import crud


class VendorOrchestrator:
    """
    هماهنگ‌کننده اصلی برای مدیریت sync تمام فروشگاه‌ها
    """
    
    def __init__(self, headless: bool = True, save_to_db: bool = True):
        """
        Args:
            headless: اجرای browser بدون نمایش UI
            save_to_db: ذخیره داده‌ها در دیتابیس
        """
        self.headless = headless
        self.save_to_db = save_to_db
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
    
    def _save_to_database(self, vendor_name: str, result: Dict) -> Dict:
        """
        ذخیره نتایج sync در دیتابیس
        
        Args:
            vendor_name: نام فروشگاه
            result: نتایج sync
            
        Returns:
            Dict با آمار ذخیره‌سازی
        """
        if not result.get("success"):
            return {"saved": False, "reason": "sync_failed"}
        
        try:
            with get_db() as db:
                # ایجاد/دریافت vendor
                vendor_display_names = {
                    'mihanstore': 'میهن استور',
                    'manamod': 'منامد',
                    'memarket': 'می‌مارکت'
                }
                
                vendor = crud.get_or_create_vendor(
                    db, 
                    name=vendor_name,
                    display_name=vendor_display_names.get(vendor_name, vendor_name.title())
                )
                
                # ذخیره سفارشات
                orders = result.get("orders", [])
                if orders:
                    db_result = crud.bulk_upsert_orders(db, vendor_name, orders)
                    console.print(f"[green]✓ Saved to DB: {db_result['new']} new, {db_result['updated']} updated orders[/green]")
                else:
                    db_result = {"new": 0, "updated": 0, "total": 0}
                
                # ذخیره آمار روزانه
                stats = result.get("stats", {})
                if stats:
                    crud.save_daily_stats(
                        db,
                        vendor_name=vendor_name,
                        stats_date=datetime.now(),
                        stats_data=stats
                    )
                    console.print(f"[green]✓ Daily stats saved to DB[/green]")
                
                return {
                    "saved": True,
                    "orders_new": db_result['new'],
                    "orders_updated": db_result['updated'],
                    "stats_saved": bool(stats)
                }
                
        except Exception as e:
            console.print(f"[red]✗ Database save error: {e}[/red]")
            return {"saved": False, "error": str(e)}
    
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
        sync_log_id = None
        
        try:
            console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
            console.print(f"[bold cyan]🔄 Syncing: {vendor_name.upper()}[/bold cyan]")
            console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
            
            # ساخت sync log
            if self.save_to_db:
                with get_db() as db:
                    crud.get_or_create_vendor(
                        db, 
                        name=vendor_name,
                        display_name=vendor_name.title()
                    )
                    sync_log = crud.create_sync_log(db, vendor_name, sync_type="full")
                    sync_log_id = sync_log.id
            
            # اجرای sync
            result = await connector.sync_all_data()
            
            # ذخیره نتیجه
            self.results[vendor_name] = result
            
            # ذخیره در DB
            if self.save_to_db and result.get("success"):
                db_result = self._save_to_database(vendor_name, result)
                result["database"] = db_result
                
                # بروزرسانی sync log
                if sync_log_id:
                    with get_db() as db:
                        crud.complete_sync_log(
                            db,
                            sync_log_id=sync_log_id,
                            status="success",
                            orders_synced=len(result.get("orders", [])),
                            new_orders=db_result.get("orders_new", 0),
                            updated_orders=db_result.get("orders_updated", 0)
                        )
            
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
            
            # بروزرسانی sync log با خطا
            if sync_log_id and self.save_to_db:
                with get_db() as db:
                    crud.complete_sync_log(
                        db,
                        sync_log_id=sync_log_id,
                        status="failed",
                        error_message=str(e)
                    )
            
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
            "saved_to_db": self.save_to_db,
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
        if self.save_to_db:
            console.print(f"[cyan]💾 Database: Enabled[/cyan]")
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
        
        return summary
    
    def get_unified_stats(self, from_db: bool = False) -> Dict:
        """
        دریافت آمار یکپارچه از تمام فروشگاه‌ها
        
        Args:
            from_db: دریافت از دیتابیس یا حافظه
            
        Returns:
            Dict با آمار ترکیبی
        """
        if from_db:
            # دریافت از دیتابیس
            try:
                with get_db() as db:
                    unified = {
                        "timestamp": datetime.now().isoformat(),
                        "total_orders": 0,
                        "total_revenue": 0,
                        "total_balance": 0,
                        "vendors_detail": {},
                        "source": "database"
                    }
                    
                    vendors = crud.list_vendors(db)
                    for vendor in vendors:
                        stats = crud.get_order_stats(db, vendor.name)
                        latest = crud.get_latest_stats(db, vendor.name)
                        
                        unified["total_orders"] += stats["total_orders"]
                        unified["total_revenue"] += stats["total_commission"]
                        
                        if latest:
                            unified["total_balance"] += latest.balance
                            unified["vendors_detail"][vendor.name] = {
                                "orders_count": stats["total_orders"],
                                "commission": stats["total_commission"],
                                "balance": latest.balance,
                                "last_sync": latest.date.isoformat()
                            }
                    
                    return unified
            except Exception as e:
                console.print(f"[red]✗ Database error: {e}[/red]")
                return {"error": str(e)}
        
        # دریافت از حافظه
        if not self.results:
            return {
                "error": "No sync results available. Run sync_all_vendors() first."
            }
        
        unified = {
            "timestamp": datetime.now().isoformat(),
            "total_orders": 0,
            "total_revenue": 0,
            "total_balance": 0,
            "vendors_detail": {},
            "source": "memory"
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

async def sync_all(save_db: bool = True):
    """کمند: همگام‌سازی همه فروشگاه‌ها"""
    orchestrator = VendorOrchestrator(headless=True, save_to_db=save_db)
    summary = await orchestrator.sync_all_vendors()
    
    # نمایش آمار یکپارچه
    unified = orchestrator.get_unified_stats(from_db=save_db)
    
    console.print("\n[bold green]📈 UNIFIED STATISTICS[/bold green]")
    console.print(f"Total Orders: {unified.get('total_orders', 0)}")
    console.print(f"Total Revenue: {unified.get('total_revenue', 0):,} تومان")
    console.print(f"Total Balance: {unified.get('total_balance', 0):,} تومان")
    
    return summary


async def sync_vendor(vendor_name: str, save_db: bool = True):
    """کمند: همگام‌سازی یک فروشگاه"""
    orchestrator = VendorOrchestrator(headless=True, save_to_db=save_db)
    orchestrator._init_connectors()
    
    result = await orchestrator.sync_single_vendor(vendor_name)
    return result


async def test_logins():
    """کمند: تست login همه فروشگاه‌ها"""
    orchestrator = VendorOrchestrator(headless=False, save_to_db=False)
    results = await orchestrator.test_all_logins()
    return results


async def show_stats(from_db: bool = True):
    """کمند: نمایش آمار از دیتابیس"""
    orchestrator = VendorOrchestrator(headless=True, save_to_db=False)
    stats = orchestrator.get_unified_stats(from_db=from_db)
    
    console.print("\n[bold green]📈 DATABASE STATISTICS[/bold green]")
    console.print(f"Total Orders: {stats.get('total_orders', 0)}")
    console.print(f"Total Revenue: {stats.get('total_revenue', 0):,} تومان")
    console.print(f"Total Balance: {stats.get('total_balance', 0):,} تومان")
    console.print(f"\nVendors Detail:")
    for vendor, detail in stats.get('vendors_detail', {}).items():
        console.print(f"  {vendor}: {detail.get('orders_count', 0)} orders")
    
    return stats


# ==================== Main ====================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m app.orchestrator sync-all          # Sync all vendors + save to DB")
        print("  python -m app.orchestrator sync <vendor>     # Sync specific vendor")
        print("  python -m app.orchestrator test-logins       # Test all logins")
        print("  python -m app.orchestrator stats             # Show stats from DB")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "sync-all":
        asyncio.run(sync_all(save_db=True))
    elif command == "sync" and len(sys.argv) >= 3:
        vendor = sys.argv[2]
        asyncio.run(sync_vendor(vendor, save_db=True))
    elif command == "test-logins":
        asyncio.run(test_logins())
    elif command == "stats":
        asyncio.run(show_stats(from_db=True))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
