# Control - Multi-Agent Business Automation System

یک سیستم خودکار مدیریت کسب‌وکار آنلاین با استفاده از چندین AI Agent برای مدیریت و مراقبت از تمام پلتفرم‌های فروش، شبکه‌های اجتماعی و پیام‌رسان‌ها.

## 🎯 اهداف پروژه

- ✅ مدیریت خودکار تمام سایت‌های فروش
- ✅ پاسخگویی خودکار به پیام‌ها
- ✅ مدیریت هم‌زمان 3 سایت افیلییت
- ✅ پنل کنترل متمرکز برای نظارت و کنترل
- ✅ گزارش‌دهی و آنالیتیکس

## 📊 معماری سیستم

### Marketplace Agents
- DivarAgent - دیوار
- SheypoorAgent - شیپور
- PindoAgent - پیندو
- BasalamAgent - بسلام
- TorobAgent - ترب

### Social Media Agents
- InstagramAgent - اینستاگرام
- TwitterAgent - توییتر
- TikTokAgent - تیک‌تاک

### Messaging Platform Agents
- TelegramAgent - تلگرام
- WhatsAppAgent - واتساپ
- RubikaAgent - روبیکا
- VirastyAgent - ویراستی
- EitaaAgent - ایتا
- BaleAgent - بله
- iGapAgent - آی‌گپ
- GapAgent - گپ

### Affiliate Marketing Agents
- ManamodAgent - مناموج
- MihanStoreAgent - میهن‌استور
- MemarketAgent - مه‌مارکت

## 🏗️ ساختار پروژه

```
control/
├── agents/
│   ├── marketplace/
│   ├── social/
│   ├── messaging/
│   └── affiliate/
├── core/
│   ├── orchestrator.py
│   ├── task_scheduler.py
│   └── event_bus.py
├── dashboard/
│   ├── web_panel.py
│   └── api/
├── storage/
│   ├── database.py
│   └── cache.py
├── config/
│   ├── credentials.json
│   └── settings.yaml
└── tests/
```

## 🛠️ تکنولوژی‌های مورد استفاده

- **Backend**: Python, FastAPI
- **Task Queue**: Celery, Redis
- **Database**: PostgreSQL/MongoDB
- **AI Framework**: LangChain
- **Web Automation**: Selenium/Playwright
- **Frontend**: React/Vue.js

## 📚 مراحل پیاده‌سازی

### Phase 1: Infrastructure (Infrastructure Setup)
- [ ] Core Orchestrator
- [ ] Database Schema
- [ ] Base Agent Class
- [ ] Task Queue Setup

### Phase 2: Marketplace Agents
- [ ] Divar Agent
- [ ] Sheypoor Agent
- [ ] Basalam Agent
- [ ] Others

### Phase 3: Messaging Agents
- [ ] Telegram Agent
- [ ] WhatsApp Agent
- [ ] Others

### Phase 4: Social & Affiliate
- [ ] Instagram Agent
- [ ] Affiliate Agents
- [ ] Others

### Phase 5: Dashboard & Monitoring
- [ ] Web Dashboard
- [ ] Real-time Monitoring
- [ ] Analytics

## 🚀 شروع سریع

```bash
# Clone repository
git clone https://github.com/shily-billy/control.git
cd control

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp config/example.env .env

# Run system
python -m control
```

## 📝 نویسنده

shily-billy (شایان)

## 📄 لایسنس

MIT License
