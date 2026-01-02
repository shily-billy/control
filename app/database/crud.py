# app/database/crud.py
"""
CRUD operations برای دیتابیس
"""
from typing import List, Optional, Dict
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.database.models import Vendor, Order, DailyStats, SyncLog
from app.common.log import console


# ==================== Vendor CRUD ====================

def create_vendor(db: Session, name: str, display_name: str, base_url: str = "") -> Vendor:
    """ساخت فروشگاه جدید"""
    vendor = Vendor(
        name=name,
        display_name=display_name,
        base_url=base_url,
        is_active=True
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


def get_vendor(db: Session, name: str) -> Optional[Vendor]:
    """دریافت فروشگاه بر اساس نام"""
    return db.query(Vendor).filter(Vendor.name == name).first()


def get_or_create_vendor(db: Session, name: str, display_name: str, base_url: str = "") -> Vendor:
    """دریافت یا ساخت فروشگاه"""
    vendor = get_vendor(db, name)
    if not vendor:
        vendor = create_vendor(db, name, display_name, base_url)
        console.print(f"[green]✓ Created vendor: {name}[/green]")
    return vendor


def list_vendors(db: Session, active_only: bool = True) -> List[Vendor]:
    """لیست تمام فروشگاه‌ها"""
    query = db.query(Vendor)
    if active_only:
        query = query.filter(Vendor.is_active == True)
    return query.all()


# ==================== Order CRUD ====================

def upsert_order(db: Session, vendor_name: str, order_data: Dict) -> tuple[Order, bool]:
    """
    ایجاد یا بروزرسانی سفارش
    
    Returns:
        (Order, is_new): شی سفارش و آیا جدید است
    """
    vendor = get_vendor(db, vendor_name)
    if not vendor:
        raise ValueError(f"Vendor '{vendor_name}' not found")
    
    order_id = order_data.get('order_id')
    if not order_id:
        raise ValueError("order_id is required")
    
    # جستجوی سفارش موجود
    existing = db.query(Order).filter(
        and_(
            Order.vendor_id == vendor.id,
            Order.order_id == order_id
        )
    ).first()
    
    if existing:
        # بروزرسانی
        for key, value in order_data.items():
            if key == 'order_id':
                continue
            if hasattr(existing, key):
                setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing, False
    else:
        # ایجاد جدید
        order = Order(
            vendor_id=vendor.id,
            order_id=order_id,
            product_name=order_data.get('product'),
            commission=order_data.get('commission_amount', 0.0),
            price=order_data.get('price', 0.0),
            status=order_data.get('status'),
            tracking_code=order_data.get('tracking_code'),
            order_date=order_data.get('date'),
            extra_data=order_data.get('extra_data', {})
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order, True


def bulk_upsert_orders(db: Session, vendor_name: str, orders_data: List[Dict]) -> Dict:
    """
    ایجاد یا بروزرسانی دسته‌جمعی سفارشات
    
    Returns:
        Dict: {تعداد جدید, تعداد بروز شده}
    """
    new_count = 0
    updated_count = 0
    errors = []
    
    for order_data in orders_data:
        try:
            order, is_new = upsert_order(db, vendor_name, order_data)
            if is_new:
                new_count += 1
            else:
                updated_count += 1
        except Exception as e:
            errors.append(str(e))
    
    return {
        "new": new_count,
        "updated": updated_count,
        "total": new_count + updated_count,
        "errors": errors
    }


def get_orders(
    db: Session, 
    vendor_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Order]:
    """دریافت لیست سفارشات"""
    query = db.query(Order)
    
    if vendor_name:
        vendor = get_vendor(db, vendor_name)
        if vendor:
            query = query.filter(Order.vendor_id == vendor.id)
    
    if status:
        query = query.filter(Order.status == status)
    
    query = query.order_by(desc(Order.order_date))
    return query.limit(limit).offset(offset).all()


def get_order_stats(db: Session, vendor_name: Optional[str] = None) -> Dict:
    """دریافت آمار سفارشات"""
    query = db.query(
        func.count(Order.id).label('total'),
        func.sum(Order.commission).label('total_commission'),
        func.sum(Order.price).label('total_price')
    )
    
    if vendor_name:
        vendor = get_vendor(db, vendor_name)
        if vendor:
            query = query.filter(Order.vendor_id == vendor.id)
    
    result = query.first()
    
    return {
        "total_orders": result.total or 0,
        "total_commission": float(result.total_commission or 0),
        "total_price": float(result.total_price or 0)
    }


# ==================== DailyStats CRUD ====================

def save_daily_stats(
    db: Session,
    vendor_name: str,
    stats_date: datetime,
    stats_data: Dict
) -> DailyStats:
    """ذخیره آمار روزانه"""
    vendor = get_vendor(db, vendor_name)
    if not vendor:
        raise ValueError(f"Vendor '{vendor_name}' not found")
    
    # حذف timestamp برای تاریخ خالص
    stats_date = stats_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # جستجوی آمار موجود
    existing = db.query(DailyStats).filter(
        and_(
            DailyStats.vendor_id == vendor.id,
            DailyStats.date == stats_date
        )
    ).first()
    
    if existing:
        # بروزرسانی
        existing.total_orders = stats_data.get('total_orders', 0)
        existing.today_orders = stats_data.get('today_orders', 0)
        existing.total_revenue = stats_data.get('total_revenue', 0.0)
        existing.balance = stats_data.get('balance', 0.0)
        existing.withdrawable = stats_data.get('withdrawable_revenue', 0.0)
        existing.detailed_stats = stats_data
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # ایجاد جدید
        daily_stats = DailyStats(
            vendor_id=vendor.id,
            date=stats_date,
            total_orders=stats_data.get('total_orders', 0),
            today_orders=stats_data.get('today_orders', 0),
            total_revenue=stats_data.get('total_revenue', 0.0),
            balance=stats_data.get('balance', 0.0),
            withdrawable=stats_data.get('withdrawable_revenue', 0.0),
            detailed_stats=stats_data
        )
        db.add(daily_stats)
        db.commit()
        db.refresh(daily_stats)
        return daily_stats


def get_latest_stats(db: Session, vendor_name: str) -> Optional[DailyStats]:
    """دریافت آخرین آمار روزانه"""
    vendor = get_vendor(db, vendor_name)
    if not vendor:
        return None
    
    return db.query(DailyStats).filter(
        DailyStats.vendor_id == vendor.id
    ).order_by(desc(DailyStats.date)).first()


def get_stats_range(
    db: Session,
    vendor_name: str,
    start_date: datetime,
    end_date: datetime
) -> List[DailyStats]:
    """دریافت آمار در بازه زمانی"""
    vendor = get_vendor(db, vendor_name)
    if not vendor:
        return []
    
    return db.query(DailyStats).filter(
        and_(
            DailyStats.vendor_id == vendor.id,
            DailyStats.date >= start_date,
            DailyStats.date <= end_date
        )
    ).order_by(DailyStats.date).all()


# ==================== SyncLog CRUD ====================

def create_sync_log(
    db: Session,
    vendor_name: str,
    sync_type: str = "full",
    metadata: Optional[Dict] = None
) -> SyncLog:
    """ساخت لاگ جدید برای sync"""
    vendor = get_vendor(db, vendor_name)
    if not vendor:
        raise ValueError(f"Vendor '{vendor_name}' not found")
    
    sync_log = SyncLog(
        vendor_id=vendor.id,
        sync_type=sync_type,
        status="running",
        started_at=datetime.utcnow(),
        metadata=metadata or {}
    )
    db.add(sync_log)
    db.commit()
    db.refresh(sync_log)
    return sync_log


def complete_sync_log(
    db: Session,
    sync_log_id: int,
    status: str,
    orders_synced: int = 0,
    new_orders: int = 0,
    updated_orders: int = 0,
    error_message: Optional[str] = None
) -> SyncLog:
    """تکمیل لاگ sync"""
    sync_log = db.query(SyncLog).filter(SyncLog.id == sync_log_id).first()
    if not sync_log:
        raise ValueError(f"SyncLog {sync_log_id} not found")
    
    sync_log.status = status
    sync_log.completed_at = datetime.utcnow()
    sync_log.duration_seconds = (sync_log.completed_at - sync_log.started_at).total_seconds()
    sync_log.orders_synced = orders_synced
    sync_log.new_orders = new_orders
    sync_log.updated_orders = updated_orders
    sync_log.error_message = error_message
    
    db.commit()
    db.refresh(sync_log)
    return sync_log


def get_sync_history(
    db: Session,
    vendor_name: Optional[str] = None,
    limit: int = 50
) -> List[SyncLog]:
    """دریافت تاریخچه sync"""
    query = db.query(SyncLog)
    
    if vendor_name:
        vendor = get_vendor(db, vendor_name)
        if vendor:
            query = query.filter(SyncLog.vendor_id == vendor.id)
    
    return query.order_by(desc(SyncLog.started_at)).limit(limit).all()
