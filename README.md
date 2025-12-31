# Control - Multi-Agent Management System

## Overview
سیستم مدیریت خودکار چند عاملی برای مدیریت همزمان:
- بازارهای آنلاین (دیوار، شیپور، پیندو، بسلام، ترب)
- شبکه‌های اجتماعی (اینستاگرام، توییتر، تیک‌تاک)
- پیام‌رسان‌ها (تلگرام، واتساپ، روبیکا و...)
- سیستم‌های افیلیت مارکتینگ

## Features
- ✅ مدیریت خودکار محصولات در همه پلتفرم‌ها
- ✅ پاسخگویی خودکار به مشتریان
- ✅ همگام‌سازی موجودی و قیمت‌ها
- ✅ پنل کنترل مرکزی
- ✅ گزارش‌دهی و تحلیل آماری
- ✅ زمان‌بندی هوشمند پست‌ها

## Architecture
```
Control System
├── Marketplace Agents (5)
├── Social Media Agents (3)
├── Messaging Agents (9)
└── Affiliate Marketing Agents (3)
```

## Installation
```bash
git clone https://github.com/shily-billy/control.git
cd control
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Quick Start
```bash
python -m control
```

## Configuration
1. Copy `config/credentials.example.json` to `config/credentials.json`
2. Fill in your credentials for each platform
3. Configure settings in `config/settings.yaml`

## Project Status
🚧 Under Active Development

## License
MIT License

## Author
shily-billy
