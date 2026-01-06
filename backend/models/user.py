from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    AFFILIATE = "affiliate"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    password_hash = Column(String)
    
    # Profile
    full_name = Column(String)
    avatar = Column(String)
    
    # Role
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Telegram
    telegram_id = Column(String, unique=True, index=True)
    telegram_username = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    addresses = relationship("Address", back_populates="user")

class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    full_name = Column(String)
    phone = Column(String)
    province = Column(String)
    city = Column(String)
    address = Column(String)
    postal_code = Column(String)
    
    is_default = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="addresses")
