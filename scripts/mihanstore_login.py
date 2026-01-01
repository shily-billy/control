import os
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    base = os.getenv("MIHANSTORE_PARTNER_URL", "https://mihanstore.net/partner/index.php")
    username = os.getenv("MIHANSTORE_USERNAME")
    password = os.getenv("MIHANSTORE_PASSWORD")

    if not username or not password:
        raise SystemExit("Set MIHANSTORE_USERNAME and MIHANSTORE_PASSWORD in your .env")

    auth_dir = Path("playwright") / ".auth"
    auth_dir.mkdir(parents=True, exist_ok=True)
    state_path = auth_dir / "mihanstore.json"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(f"{base}?act=logins", wait_until="domcontentloaded")

        # Exact fields from login HTML:
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)

        # CAPTCHA is required on this login form (captcha.php + captcha_code).
        # Do not attempt to bypass; instead, switch to manual/headful flow.
        if page.locator('input[name="captcha_code"]').count() > 0:
            browser.close()
            raise SystemExit(
                "CAPTCHA detected. Use scripts/mihanstore_login_manual.py to login in headful mode and type captcha manually."
            )

        page.click('input[name="submit"]')
        page.wait_for_timeout(2000)

        context.storage_state(path=str(state_path))
        browser.close()

    print(f"Saved auth state to: {state_path}")


if __name__ == "__main__":
    main()
