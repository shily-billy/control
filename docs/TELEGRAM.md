## Telegram (Webhook)

This project includes a webhook-based Telegram bot handler.

1) Set env:
- `TELEGRAM_BOT_TOKEN`

2) Run locally:
```bash
docker compose up --build
```

3) Set Telegram webhook (needs public HTTPS URL):
- `https://api.telegram.org/bot<token>/setWebhook?url=https://<your-domain>/telegram/webhook`

Endpoint in this app:
- `POST /telegram/webhook`

Note: For local development without public HTTPS, use polling temporarily or use a tunnel (ngrok/cloudflared). Webhooks are typically preferred for production deployments. [web:98][web:103]
