## Vendor/Affiliate Integration (3 sources)

This project can populate the Telegram catalog by syncing from 3 affiliate/vendor sites using web automation (Playwright).

### How it works
- Each vendor implements `fetch_products()`.
- A Celery task `control.sync_vendors` runs the sync.
- API endpoint `POST /catalog/sync` enqueues the sync task.
- Telegram `/catalog` and `/product` display the local catalog.

### Notes & Risk
- For scraping/automation, respect the target site ToS and robots.txt and use rate limiting to avoid disruption. [web:140][web:142]

### Next
- Replace placeholder selectors (`[data-product-card]`, `.title`, `.price`) with real selectors per site.
- Add login flows (persistent context is already used per vendor user_data_dir).
