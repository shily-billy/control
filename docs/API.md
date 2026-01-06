# 📚 مستندات API - DOT SHOP

## Base URL
```
http://localhost:8000/api
```

## Authentication

برای درخواست‌های نیازمند احراز هویت، توکن JWT را در header ارسال کنید:

```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Products API

### جستجوی محصولات

```http
GET /api/products/search?q={query}
```

**پارامترها:**
- `q` (required): عبارت جستجو
- `platform` (optional): نام پلتفرم خاص (digikala, mihanstore, etc.)

**پاسخ موفق:**
```json
{
  "query": "کفش ورزشی",
  "recommended": {
    "platform": "mihanstore",
    "product": {
      "id": "12345",
      "title": "کفش ورزشی نایک",
      "price": 850,
      "image": "https://..."
    },
    "commission": 340,
    "commission_rate": 0.40
  },
  "all_platforms": {...}
}
```

### دریافت لیست محصولات

```http
GET /api/products?skip=0&limit=50
```

### دریافت یک محصول

```http
GET /api/products/{product_id}
```

---

## Orders API

### ایجاد سفارش

```http
POST /api/orders/create
```

**بدنه درخواست:**
```json
{
  "user_id": 1,
  "items": [
    {
      "product_id": 1,
      "name": "کفش ورزشی",
      "price": 850,
      "quantity": 1,
      "platform": "mihanstore",
      "commission_rate": 0.40
    }
  ],
  "shipping_address": {
    "full_name": "علی احمدی",
    "phone": "09123456789",
    "address": "تهران، ...",
    "postal_code": "1234567890"
  }
}
```

### پیگیری سفارش

```http
GET /api/orders/track/{order_number}
```

**پاسخ:**
```json
{
  "order_number": "DS-12345678",
  "status": "shipped",
  "tracking_number": "POST-9876543",
  "items": [...]
}
```

---

## Users API

### ثبت‌نام

```http
POST /api/users/register
```

**بدنه:**
```json
{
  "phone": "09123456789",
  "password": "secure_password",
  "full_name": "علی احمدی",
  "email": "ali@example.com"
}
```

### ورود

```http
POST /api/users/login
```

**بدنه:**
```json
{
  "phone": "09123456789",
  "password": "secure_password"
}
```

**پاسخ:**
```json
{
  "success": true,
  "token": "eyJhbGc...",
  "user": {
    "id": 1,
    "phone": "09123456789",
    "full_name": "علی احمدی"
  }
}
```

---

## Dashboard API

### آمار داشبورد

```http
GET /api/dashboard/stats
```

**پاسخ:**
```json
{
  "today": {
    "orders": 15,
    "sales": 12500,
    "commission": 3750
  },
  "week": {
    "orders": 98
  },
  "totals": {
    "products": 542,
    "users": 1234
  }
}
```

### نمودار فروش

```http
GET /api/dashboard/sales-chart?days=7
```

---

## Platforms API

### لیست پلتفرم‌ها

```http
GET /api/platforms
```

### نرخ کمیسیون‌ها

```http
GET /api/platforms/commissions
```

**پاسخ:**
```json
{
  "digikala": {
    "commission_rate": 0.12,
    "commission_percent": "12%"
  },
  "mihanstore": {
    "commission_rate": 0.40,
    "commission_percent": "40%"
  }
}
```

---

## کدهای خطا

- `200` - موفق
- `400` - درخواست نامعتبر
- `401` - نیاز به احراز هویت
- `403` - دسترسی رد شد
- `404` - یافت نشد
- `500` - خطای سرور
