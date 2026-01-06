# 🚀 راهنمای دیپلوی DOT SHOP

## دیپلوی روی VPS (Ubuntu 22.04)

### مرحله 1: نصب پیش‌نیازها

```bash
# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# نصب Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# نصب Docker Compose
sudo apt install docker-compose -y

# نصب Git
sudo apt install git -y

# نصب Nginx
sudo apt install nginx -y
```

### مرحله 2: کلون پروژه

```bash
# کلون از GitHub
git clone https://github.com/shily-billy/control.git dotshop
cd dotshop

# کپی فایل تنظیمات
cp config/.env.example config/.env
```

### مرحله 3: تنظیمات محیطی

```bash
# ویرایش فایل .env
nano config/.env
```

**تنظیمات مهم:**

```env
# دامنه
SHOP_DOMAIN=yourdomain.com

# دیتابیس (رمز قوی بگذارید!)
DB_PASSWORD=your_very_secure_password_here

# امنیت (حتماً تغییر دهید!)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# تلگرام
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ADMIN_ID=your_telegram_id

# پلتفرم‌ها
DIGIKALA_AFFILIATE_ID=your_digikala_id
MIHANSTORE_PARTNER_ID=your_mihanstore_id
```

### مرحله 4: راه‌اندازی با Docker

```bash
# ساخت و اجرای کانتینرها
docker-compose up -d

# بررسی وضعیت
docker-compose ps

# مشاهده لاگ‌ها
docker-compose logs -f
```

### مرحله 5: تنظیم دامنه و SSL

#### تنظیم DNS
در پنل دامنه خود، یک رکورد A اضافه کنید:
```
Type: A
Name: @
Value: IP_SERVER_SHOMA
```

#### نصب SSL با Certbot

```bash
# نصب Certbot
sudo apt install certbot python3-certbot-nginx -y

# دریافت گواهی SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# تنظیم تمدید خودکار
sudo systemctl enable certbot.timer
```

### مرحله 6: تنظیم Nginx

```bash
# ایجاد فایل کانفیگ
sudo nano /etc/nginx/sites-available/dotshop
```

محتوای فایل:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# فعال‌سازی سایت
sudo ln -s /etc/nginx/sites-available/dotshop /etc/nginx/sites-enabled/

# تست کانفیگ
sudo nginx -t

# ریستارت Nginx
sudo systemctl restart nginx
```

## دیپلوی روی Hostinger/cPanel

### مرحله 1: آپلود فایل‌ها

1. فایل‌های پروژه را zip کنید
2. از File Manager در cPanel آپلود کنید
3. Extract کنید

### مرحله 2: تنظیم Python App

1. برو به Python App در cPanel
2. Create Application
3. Python Version: 3.11
4. App Root: `/home/username/dotshop/backend`
5. App URL: `/api`

### مرحله 3: تنظیم Node.js

1. برو به Node.js App
2. Create Application  
3. Node.js Version: 18.x
4. App Root: `/home/username/dotshop/frontend`
5. App URL: `/`

## نگهداری و Monitoring

### بکاپ خودکار

```bash
# ایجاد اسکریپت بکاپ
nano /root/backup-dotshop.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backups/dotshop"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# بکاپ دیتابیس
docker exec dotshop_postgres pg_dump -U dotshop_user dotshop > $BACKUP_DIR/db-$DATE.sql

# بکاپ فایل‌ها
tar -czf $BACKUP_DIR/files-$DATE.tar.gz /path/to/dotshop

# حذف بکاپ‌های قدیمی (بیش از 30 روز)
find $BACKUP_DIR -type f -mtime +30 -delete
```

```bash
# اجازه اجرا
chmod +x /root/backup-dotshop.sh

# اضافه کردن به cron (هر روز ساعت 2 صبح)
crontab -e
```

اضافه کنید:
```
0 2 * * * /root/backup-dotshop.sh
```

### مانیتورینگ

```bash
# نصب htop برای مانیتور منابع
sudo apt install htop -y

# مشاهده استفاده از منابع
htop

# بررسی لاگ‌ها
docker-compose logs -f --tail=100

# بررسی وضعیت دیسک
df -h

# بررسی وضعیت RAM
free -h
```

## به‌روزرسانی

```bash
cd /path/to/dotshop

# دریافت آخرین تغییرات
git pull origin main

# ریبیلد کانتینرها
docker-compose down
docker-compose build
docker-compose up -d
```

## عیب‌یابی

### مشکلات رایج:

**1. دیتابیس کانکت نمی‌شود:**
```bash
# بررسی وضعیت PostgreSQL
docker-compose logs postgres

# ریستارت
docker-compose restart postgres
```

**2. ربات تلگرام کار نمی‌کند:**
```bash
# بررسی توکن
cat config/.env | grep TELEGRAM

# بررسی لاگ
docker-compose logs telegram-bot
```

**3. کمبود حافظه:**
```bash
# پاک کردن کانتینرهای قدیمی
docker system prune -a

# بررسی منابع
docker stats
```
