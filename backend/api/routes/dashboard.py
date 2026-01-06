from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import get_db
from models.order import Order, OrderStatus
from models.product import Product
from models.user import User
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    آمار داشبورد
    """
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # تعداد سفارشات امروز
    today_orders = db.query(Order).filter(
        func.date(Order.created_at) == today
    ).count()
    
    # تعداد سفارشات هفته
    week_orders = db.query(Order).filter(
        Order.created_at >= week_ago
    ).count()
    
    # فروش امروز
    today_sales = db.query(func.sum(Order.total)).filter(
        func.date(Order.created_at) == today,
        Order.status != OrderStatus.CANCELLED
    ).scalar() or 0
    
    # کمیسیون امروز
    today_commission = db.query(func.sum(Order.commission_amount)).filter(
        func.date(Order.created_at) == today,
        Order.status != OrderStatus.CANCELLED
    ).scalar() or 0
    
    # تعداد محصولات
    total_products = db.query(Product).count()
    
    # تعداد کاربران
    total_users = db.query(User).count()
    
    return {
        "today": {
            "orders": today_orders,
            "sales": today_sales,
            "commission": today_commission
        },
        "week": {
            "orders": week_orders
        },
        "totals": {
            "products": total_products,
            "users": total_users
        }
    }

@router.get("/sales-chart")
def get_sales_chart(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    نمودار فروش
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    daily_sales = db.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total).label('total'),
        func.sum(Order.commission_amount).label('commission'),
        func.count(Order.id).label('orders')
    ).filter(
        Order.created_at >= start_date,
        Order.status != OrderStatus.CANCELLED
    ).group_by(
        func.date(Order.created_at)
    ).all()
    
    return {
        "labels": [str(s.date) for s in daily_sales],
        "sales": [float(s.total) for s in daily_sales],
        "commissions": [float(s.commission) for s in daily_sales],
        "orders": [s.orders for s in daily_sales]
    }

@router.get("/top-products")
def get_top_products(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    محصولات پرفروش
    """
    products = db.query(Product).order_by(
        Product.sales_count.desc()
    ).limit(limit).all()
    
    return {"products": products}
