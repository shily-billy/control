from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    discount_percent = Column(Float, default=0)
    
    # Images
    main_image = Column(String)
    images = Column(JSON)  # Array of image URLs
    
    # Category
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")
    
    # Stock
    in_stock = Column(Boolean, default=True)
    quantity = Column(Integer, default=0)
    
    # SEO
    meta_title = Column(String)
    meta_description = Column(Text)
    meta_keywords = Column(String)
    
    # Platform availability
    platforms = Column(JSON)  # {"digikala": {...}, "mihanstore": {...}}
    
    # Stats
    views = Column(Integer, default=0)
    sales_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = relationship("OrderItem", back_populates="product")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    icon = Column(String)
    image = Column(String)
    description = Column(Text)
    
    # Relationships
    products = relationship("Product", back_populates="category")
    children = relationship("Category")
    
    created_at = Column(DateTime, default=datetime.utcnow)
