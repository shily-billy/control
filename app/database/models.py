# app/database/models.py
"""
مدل‌های دیتابیس برای ذخیره داده‌های فروشگاه‌ها
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Vendor(Base):
    """
    جدول فروشگاه‌ها
    """
    __tablename__ = 'vendors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)  # mihanstore, manamod, ...
    display_name = Column(String(100), nullable=False)  # نام فارسی
    base_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = relationship('Order', back_populates='vendor', cascade='all, delete-orphan')
    stats = relationship('DailyStats', back_populates='vendor', cascade='all, delete-orphan')
    sync_logs = relationship('SyncLog', back_populates='vendor', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Vendor(name='{self.name}', active={self.is_active})>"


class Order(Base):
    """
    جدول سفارشات
    """
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    
    # اطلاعات اصلی
    order_id = Column(String(100), nullable=False)  # شناسه سفارش در فروشگاه
    product_name = Column(Text)
    commission = Column(Float, default=0.0)  # سهم همکار (تومان)
    price = Column(Float, default=0.0)  # قیمت کل (تومان)
    
    # تاریخ و وضعیت
    order_date = Column(DateTime)  # تاریخ ثبت سفارش
    status = Column(String(50))  # وضعیت سفارش
    tracking_code = Column(String(100))  # کد رهگیری پستی
    
    # داده‌های اضافی (JSON)
    extra_data = Column(JSON, default={})  # فیلدهای اضافی مختص هر فروشگاه
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    vendor = relationship('Vendor', back_populates='orders')
    
    # Indexes
    __table_args__ = (
        Index('idx_vendor_order', 'vendor_id', 'order_id', unique=True),
        Index('idx_order_date', 'order_date'),
        Index('idx_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Order(id={self.order_id}, vendor={self.vendor.name if self.vendor else 'N/A'}, commission={self.commission})>"


class DailyStats(Base):
    """
    جدول آمار روزانه
    """
    __tablename__ = 'daily_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    
    # تاریخ
    date = Column(DateTime, nullable=False)  # تاریخ آمار
    
    # آمار کلی
    total_orders = Column(Integer, default=0)
    today_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)  # تومان
    balance = Column(Float, default=0.0)  # موجودی (تومان)
    withdrawable = Column(Float, default=0.0)  # قابل برداشت (تومان)
    
    # آمار تفصیلی (JSON)
    detailed_stats = Column(JSON, default={})  # آمارهای دقیق‌تر
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    vendor = relationship('Vendor', back_populates='stats')
    
    # Indexes
    __table_args__ = (
        Index('idx_vendor_date', 'vendor_id', 'date', unique=True),
    )
    
    def __repr__(self):
        return f"<DailyStats(vendor={self.vendor.name if self.vendor else 'N/A'}, date={self.date}, orders={self.total_orders})>"


class SyncLog(Base):
    """
    جدول لاگ همگام‌سازی‌ها
    """
    __tablename__ = 'sync_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    
    # اطلاعات sync
    sync_type = Column(String(50))  # full, orders_only, stats_only
    status = Column(String(20))  # success, failed, partial
    
    # زمان‌بندی
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    # نتایج
    orders_synced = Column(Integer, default=0)
    new_orders = Column(Integer, default=0)
    updated_orders = Column(Integer, default=0)
    
    # خطاها
    error_message = Column(Text)
    
    # داده‌های اضافی
    metadata = Column(JSON, default={})
    
    # Relationship
    vendor = relationship('Vendor', back_populates='sync_logs')
    
    # Indexes
    __table_args__ = (
        Index('idx_vendor_started', 'vendor_id', 'started_at'),
        Index('idx_status', 'status'),
    )
    
    def __repr__(self):
        return f"<SyncLog(vendor={self.vendor.name if self.vendor else 'N/A'}, status={self.status}, duration={self.duration_seconds}s)>"


# تست ساخت جداول
if __name__ == "__main__":
    from app.database.session import engine, init_db
    from app.common.log import console
    
    console.print("[cyan]Creating database tables...[/cyan]")
    init_db()
    console.print("[green]✓ Database tables created successfully![/green]")
    
    # نمایش جداول
    console.print("\n[cyan]Tables:[/cyan]")
    for table in Base.metadata.tables:
        console.print(f"  - {table}")
