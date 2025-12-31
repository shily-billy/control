## Telegram: Direct + Channel Catalog

### Direct (DM) & Groups
- Bot will respond in DMs.
- In groups, bot will receive messages depending on privacy mode/settings; commands like `/catalog` are reliable entrypoints. [web:116]

### Channel catalog
- Bot must be **admin** in the channel to post messages.
- Bots cannot legitimately read channel history unless Telegram delivers updates & permissions allow it; for catalog publishing, posting is enough. [web:120][web:118]

### Commands
- `/catalog` : list products
- `/product <SKU>` : show a product
- `/publish_catalog` : publish all products into the configured channel

### Env
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CATALOG_CHANNEL_ID` (e.g. `-1001234567890`)
