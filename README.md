# Control — Affiliate SuperPanel

این ریپو برای «سوپرپنل لوکال» (Web UI + CLI) جهت مدیریت و اتوماسیون چند پنل افیلیت/همکاری در فروش ساخته شده است.

## اهداف فاز ۱
- اجرای لوکال روی Kali Linux
- CLI برای sync/report
- Web UI روی localhost
- کانکتورهای جداگانه برای:
  - manamod (https://manamod.net/partner/dashboard)
  - mihanstore (https://mihanstore.net/partner/index.php)
  - memarketaffiliate (https://memarketaffiliate.com/login)

## اجرا (اسکلت)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.cli --help
python -m app.web
```

## امنیت
- هیچ رمز/کوکی داخل گیت ذخیره نمی‌شود.
- تنظیمات در `.env` (که در `.gitignore` است) نگهداری می‌شود.

