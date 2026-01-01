# Mihanstore Connector Documentation

## خلاصه

کانکتور Mihanstore برای استخراج خودکار آمار و سفارشات از پنل همکاری میهن استور طراحی شده است.

## قابلیت‌ها

### ✅ پیاده‌سازی شده

- **لاگین خودکار**: ورود به پنل با Playwright
- **آمار داشبورد**: استخراج 10 نوع آمار مختلف
- **لیست سفارشات**: دریافت سفارشات با جزئیات کامل
- **Sync کامل**: همگام‌سازی تمام داده‌ها در یک تراکنش

## آمار قابل استخراج

| نام فیلد | توضیحات | نوع |
|---------------|-------------|------|
| `total_orders` | تعداد کل سفارشات | int |
| `total_revenue` | درآمد کل (تومان) | int |
| `completed_orders` | سفارشات تعیین تکلیف شده | int |
| `pending_orders` | سفارشات در حال بررسی | int |
| `yesterday_orders` | سفارشات دیروز | int |
| `today_orders` | سفارشات امروز | int |
| `referral_revenue` | درآمد از بازاریابی | int |
| `paid_revenue` | درآمد پرداخت شده | int |
| `return_deduction` | کسر بابت برگشتی | int |
| `withdrawable_revenue` | درآمد قابل برداشت | int |

## جزئیات سفارشات

هر سفارش شامل این فیلدها است:

```python
{
    "order_id": "250401377095729",
    "product": "چسب قلمی حرارتی همه کاره (3 عددی)",
    "commission": "33,390 تومان",
    "commission_amount": 33390,
    "date": "1404-01-12",
    "tracking_code": None,
    "status": "انصرافی"
}
```

## نصب و پیکربندی

### 1️⃣ نصب وابستگی‌ها

```bash
pip install playwright
playwright install chromium
```

### 2️⃣ تنظیم فایل `.env`

```bash
cp .env.example .env
```

سپس اطلاعات خود را وارد کنید:

```env
MIHANSTORE_USERNAME=09123456789
MIHANSTORE_PASSWORD=your_password
```

## نحوه استفاده

### تست لاگین

```python
import asyncio
from app.connectors.mihanstore import MihanstoреConnector

async def test_login():
    connector = MihanstoреConnector(
        username="09123456789",
        password="your_password",
        headless=False  # برای حل دستی CAPTCHA
    )
    
    result = await connector.login_test()
    print(result)

asyncio.run(test_login())
```

### دریافت آمار داشبورد

```python
async def get_stats():
    connector = MihanstoреConnector(
        username="09123456789",
        password="your_password",
        headless=False
    )
    
    await connector.login()
    stats = await connector.get_dashboard_stats()
    
    print(f"تعداد سفارشات: {stats['total_orders']}")
    print(f"درآمد کل: {stats['total_revenue']:,} تومان")
    
    await connector._close_browser()

asyncio.run(get_stats())
```

### دریافت لیست سفارشات

```python
async def get_orders():
    connector = MihanstoреConnector(
        username="09123456789",
        password="your_password",
        headless=False
    )
    
    await connector.login()
    orders = await connector.get_orders(limit=20)
    
    for order in orders:
        print(f"#{order['order_id']}: {order['product']}")
        print(f"  سهم: {order['commission']}")
        print(f"  وضعیت: {order['status']}")
    
    await connector._close_browser()

asyncio.run(get_orders())
```

### Sync کامل (توصیه شده)

```python
async def full_sync():
    connector = MihanstoреConnector(
        username="09123456789",
        password="your_password",
        headless=False
    )
    
    result = await connector.sync_all_data()
    
    if result['success']:
        print(f"✅ Sync موفق")
        print(f"  • {result['orders_count']} سفارش")
        print(f"  • {result['summary']['total_revenue']:,} تومان درآمد")
    else:
        print(f"❌ Sync ناموفق: {result.get('error')}")

asyncio.run(full_sync())
```

## تست مستقیم

```bash
# اجرای تست داخلی کانکتور
python -m app.connectors.mihanstore
```

## نکات مهم

### ⚠️ CAPTCHA

سایت میهن استور در صفحه لاگین از CAPTCHA استفاده می‌کند. برای حل آن:

1. **حل دستی** (توصیه شده): `headless=False` استفاده کنید
2. **سرویس حل CAPTCHA**: مثل 2Captcha یا Anti-Captcha
3. **Cookie ذخیره شده**: بعد از لاگین موفق session را ذخیره کنید

### 🔒 امنیت

- هیچ‌وقت فایل `.env` را commit نکنید
- از environment variables استفاده کنید
- User agent و headers را عادی نگه دارید

### ⏱️ Rate Limiting

برای جلوگیری از مسدود شدن IP:

- بین درخواست‌ها تاخیر ایجاد کنید (2-5 ثانیه)
- بیش از 10 درخواست در دقیقه نداشته باشید
- در ساعات کم ترافیک sync انجام دهید

## خطایابی (Troubleshooting)

### خطا: "Login failed"

- نام کاربری و رمز عبور را بررسی کنید
- CAPTCHA را درست حل کنید
- از `headless=False` استفاده کنید

### خطا: "Timeout"

- اینترنت خود را بررسی کنید
- timeout را افزایش دهید (60000ms)
- از VPN استفاده کنید

### خطا: "Selector not found"

- ساختار سایت تغییر کرده است
- سلکتورها را بررسی و به‌روزرسانی کنید

## توسعه آینده

- [ ] پشتیبانی از session cookies برای حذف CAPTCHA
- [ ] اضافه کردن retry logic
- [ ] پشتیبانی از proxy
- [ ] لاگ جامع‌تر
- [ ] تست‌های unit و integration

## لایسنس

این کانکتور بخشی از پروژه Control SuperPanel است.

---

**توسعه دهنده**: [@shily-billy](https://github.com/shily-billy)  
**آخرین به‌روزرسانی**: 1404/10/12
