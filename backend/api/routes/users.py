from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_password_hash, verify_password, create_access_token
from models.user import User, UserRole
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter()

class UserCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    phone: str
    password: str

@router.post("/register")
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    ثبت‌نام کاربر جدید
    """
    # بررسی وجود کاربر
    existing = db.query(User).filter(User.phone == user_data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="شماره تلفن قبلاً ثبت شده است")
    
    # ایجاد کاربر جدید
    user = User(
        email=user_data.email,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=UserRole.CUSTOMER
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # ایجاد توکن
    token = create_access_token({"user_id": user.id, "phone": user.phone})
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "phone": user.phone,
            "full_name": user.full_name
        },
        "token": token
    }

@router.post("/login")
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    ورود کاربر
    """
    user = db.query(User).filter(User.phone == credentials.phone).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="شماره تلفن یا رمز عبور اشتباه است")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="حساب کاربری غیرفعال است")
    
    # ایجاد توکن
    token = create_access_token({"user_id": user.id, "phone": user.phone})
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "phone": user.phone,
            "full_name": user.full_name,
            "role": user.role
        },
        "token": token
    }

@router.get("/me")
def get_current_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    دریافت اطلاعات کاربر فعلی
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    return user
