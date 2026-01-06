from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(credentials: LoginRequest):
    # Simple demo authentication
    if credentials.username == "admin" and credentials.password == "admin123":
        return {
            "access_token": "demo_token_123",
            "token_type": "bearer"
        }
    raise HTTPException(status_code=401, detail="نام کاربری یا رمز عبور اشتباه است")

@router.post("/register")
async def register():
    return {"message": "Register - Coming Soon"}