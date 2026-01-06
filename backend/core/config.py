from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Shop Information
    SHOP_NAME: str = "فروشگاه نقطه"
    SHOP_DOMAIN: str = "dotshop.ir"
    SHOP_OWNER: str = ""
    SHOP_EMAIL: str = "info@dotshop.ir"
    SHOP_PHONE: str = ""
    
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
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    JWT_SECRET: str = "your-jwt-secret-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # API Settings
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Platform API Keys
    DIGIKALA_AFFILIATE_ID: str = ""
    DIGIKALA_API_KEY: str = ""
    DIGIKALA_COMMISSION_RATE: float = 0.12
    
    MIHANSTORE_PARTNER_ID: str = ""
    MIHANSTORE_API_KEY: str = ""
    MIHANSTORE_COMMISSION_RATE: float = 0.40
    
    BAMILO_AFFILIATE_KEY: str = ""
    BAMILO_COMMISSION_RATE: float = 0.25
    
    TOROB_API_KEY: str = ""
    
    DIVAR_API_KEY: str = ""
    SHEYPOOR_API_KEY: str = ""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ADMIN_ID: str = ""
    
    # SMS
    SMS_PROVIDER: str = "kavenegar"
    KAVENEGAR_API_KEY: str = ""
    
    # Payment
    ZARINPAL_MERCHANT_ID: str = ""
    
    # Scraper
    SCRAPER_MAX_WORKERS: int = 5
    SCRAPER_DELAY: int = 2
    SCRAPER_TIMEOUT: int = 30
    
    # Cache
    PRODUCT_CACHE_TTL: int = 1800
    PRICE_CACHE_TTL: int = 900
    
    class Config:
        env_file = "config/.env"
        case_sensitive = True

settings = Settings()