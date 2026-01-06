from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Shop Info
    SHOP_NAME: str = "فروشگاه نقطه"
    SHOP_DOMAIN: str = "dotshop.ir"
    SHOP_OWNER: str = ""
    
    # Database
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "dotshop"
    DB_USER: str = "dotshop_user"
    DB_PASSWORD: str = "change_me"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_SECRET: str = "change-this-jwt-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # Platform APIs
    DIGIKALA_AFFILIATE_ID: str = ""
    MIHANSTORE_PARTNER_ID: str = ""
    BAMILO_AFFILIATE_KEY: str = ""
    TOROB_API_KEY: str = ""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ADMIN_ID: str = ""
    
    # SMS
    KAVENEGAR_API_KEY: str = ""
    
    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    
    class Config:
        env_file = "config/.env"
        case_sensitive = True

settings = Settings()
