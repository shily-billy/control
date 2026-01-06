from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from core.database import Base

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    
    # User
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="orders")
    
    # Status
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Pricing
    subtotal = Column(Float, nullable=False)
    shipping_cost = Column(Float, default=0)
    tax = Column(Float, default=0)
    discount = Column(Float, default=0)
    total = Column(Float, nullable=False)
    
    # Commission earned
    commission_amount = Column(Float, default=0)
    commission_platform = Column(String)  # Which platform gave commission
    
    # Shipping
    shipping_address = Column(JSON)
    tracking_number = Column(String)
    
    # Payment
    payment_method = Column(String)
    payment_gateway = Column(String)
    transaction_id = Column(String)
    
    # Platform info
    source_platform = Column(String)  # telegram, instagram, website, etc.
    fulfilled_by = Column(String)  # digikala, mihanstore, etc.
    
    # Notes
    customer_notes = Column(Text)
    admin_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = Column(DateTime)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Order
    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("Order", back_populates="items")
    
    # Product
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="orders")
    
    # Details
    product_name = Column(String)
    product_image = Column(String)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float)
    total_price = Column(Float)
    
    # Platform where product was purchased from
    platform = Column(String)
    platform_product_id = Column(String)
    commission_rate = Column(Float)
    commission_amount = Column(Float)
