from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from core.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, index=True)
    description = Column(Text)
    
    # Pricing
    base_price = Column(Float, nullable=False)
    sale_price = Column(Float)
    final_price = Column(Float, nullable=False)
    
    # Images
    main_image = Column(String(500))
    images = Column(JSON)  # List of image URLs
    
    # Category
    category = Column(String(100))
    subcategory = Column(String(100))
    
    # Stock
    in_stock = Column(Boolean, default=True)
    quantity = Column(Integer, default=0)
    
    # Platform Data
    platform_data = Column(JSON)  # Store platform-specific info
    
    # Metadata
    views = Column(Integer, default=0)
    sales = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)