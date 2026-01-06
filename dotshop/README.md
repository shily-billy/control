# 🛍️ DOT SHOP - فروشگاه نقطه

## امپراتوری فروش شخصی کامل

یک فروشگاه اینترنتی کاملاً شخصی که همزمان از 10+ کانال فروش بزرگ ایران سود می‌برد.

## ویژگی‌های کلیدی

### 🎯 کانال‌های فروش
- دیجی‌کالا (9-20% کمیسیون)
- میهن استور (30-50% کمیسیون)
- ترب (مقایسه قیمت)
- دیوار (آگهی محلی)
- شیپور (خرید و فروش)
- بامیلو (25% کمیسیون)
- اینستاگرام
- تلگرام
- واتساپ
- و سایر کانال‌ها...

### 🤖 سیستم هوشمند
- انتخاب خودکار بهترین پلتفرم بر اساس کمیسیون
- هدایت نامرئی مشتری
- به‌روزرسانی خودکار قیمت‌ها
- ردیابی سفارشات

### 📱 رابط‌های کاربری
- وب‌سایت فروشگاهی مدرن
- ربات تلگرام
- پنل مدیریت
- API کامل

## نصب و راه‌اندازی

### پیش‌نیازها
```bash
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (اختیاری)
```

### نصب سریع با Docker
```bash
cd dotshop
cp .env.example .env
# فایل .env را ویرایش کنید
docker-compose up -d
```

### نصب دستی

#### 1. Backend
```bash
cd dotshop/backend
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

#### 2. Frontend
```bash
cd dotshop/frontend
npm install
npm run dev
```

#### 3. Telegram Bot
```bash
cd dotshop/telegram-bot
pip install -r requirements.txt
python bot.py
```

## تنظیمات

### فایل .env
```env
# اطلاعات پایگاه داده
DATABASE_URL=postgresql://user:password@localhost:5432/dotshop
REDIS_URL=redis://localhost:6379/0

# تنظیمات فروشگاه
SHOP_NAME=فروشگاه نقطه
SHOP_DOMAIN=dotshop.ir
SHOP_PHONE=09123456789
SHOP_EMAIL=info@dotshop.ir

# ربات تلگرام
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# اطلاعات افیلیت
DIGIKALA_AFFILIATE_ID=
MIHANSTORE_AFFILIATE_ID=
BAMILO_AFFILIATE_ID=
TOROB_API_KEY=

# پیامک
SMS_API_KEY=
SMS_SENDER=

# امنیت
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## مستندات

- [راهنمای نصب کامل](./docs/installation.md)
- [راهنمای استفاده](./docs/usage.md)
- [مستندات API](./docs/api.md)
- [راهنمای ربات تلگرام](./docs/telegram-bot.md)
- [اتصال به پلتفرم‌ها](./docs/integrations.md)

## ساختار پروژه

```
dotshop/
├── backend/              # API Backend (FastAPI)
├── frontend/             # فروشگاه (Next.js)
├── telegram-bot/         # ربات تلگرام
├── database/             # اسکیما و مایگریشن
├── scrapers/             # ماژول‌های کشیدن داده
├── docker/               # تنظیمات Docker
├── docs/                 # مستندات
└── config/               # فایل‌های کانفیگ
```

## مجوز
MIT License

## پشتیبانی
برای سوالات و مشکلات، Issue باز کنید.

---

**ساخته شده با ❤️ برای کسب‌وکارهای ایرانی**