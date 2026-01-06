from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.order import Order, OrderItem, OrderStatus
from models.user import User
from typing import List, Optional
import random
import string

router = APIRouter()

def generate_order_number():
    """تولید شماره سفارش یکتا"""
    return 'DS-' + ''.join(random.choices(string.digits, k=8))

@router.post("/create")
def create_order(
    user_id: int,
    items: List[dict],
    shipping_address: dict,
    db: Session = Depends(get_db)
):
    """
    ایجاد سفارش جدید
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    # محاسبه مجموع
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    shipping_cost = 50000 / 1000  # 50 هزار تومان
    total = subtotal + shipping_cost
    
    # محاسبه کمیسیون کل
    commission_total = 0
    for item in items:
        commission_rate = item.get('commission_rate', 0.12)
        commission_total += item['price'] * item['quantity'] * commission_rate
    
    # ایجاد سفارش
    order = Order(
        order_number=generate_order_number(),
        user_id=user_id,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        total=total,
        commission_amount=commission_total,
        shipping_address=shipping_address,
        status=OrderStatus.PENDING
    )
    
    db.add(order)
    db.flush()
    
    # اضافه کردن آیتم‌ها
    for item_data in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data.get('product_id'),
            product_name=item_data['name'],
            quantity=item_data['quantity'],
            unit_price=item_data['price'],
            total_price=item_data['price'] * item_data['quantity'],
            platform=item_data.get('platform', 'unknown'),
            commission_rate=item_data.get('commission_rate', 0.12)
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(order)
    
    return {
        "success": True,
        "order_number": order.order_number,
        "order_id": order.id,
        "total": total,
        "commission": commission_total
    }

@router.get("/")
def get_orders(
    user_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    دریافت لیست سفارشات
    """
    query = db.query(Order)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "orders": orders,
        "total": total
    }

@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """
    دریافت جزئیات سفارش
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="سفارش یافت نشد")
    
    return order

@router.get("/track/{order_number}")
def track_order(
    order_number: str,
    db: Session = Depends(get_db)
):
    """
    پیگیری سفارش با شماره سفارش
    """
    order = db.query(Order).filter(Order.order_number == order_number).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="سفارش یافت نشد")
    
    return {
        "order_number": order.order_number,
        "status": order.status,
        "tracking_number": order.tracking_number,
        "created_at": order.created_at,
        "items": order.items
    }

@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db)
):
    """
    به‌روزرسانی وضعیت سفارش
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="سفارش یافت نشد")
    
    order.status = status
    db.commit()
    
    return {"success": True, "status": status}
