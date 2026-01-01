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
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(f"{base}?act=logins", wait_until="domcontentloaded")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)

        print("CAPTCHA detected on this form. Please type the captcha in the opened browser.")
        print("Then click the login button. This script will wait until navigation happens.")

        # Wait for user to solve captcha and submit.
        page.wait_for_load_state("networkidle")

        # Give a little extra time for any redirect.
        page.wait_for_timeout(1500)

        context.storage_state(path=str(state_path))
        browser.close()

    print(f"Saved auth state to: {state_path}")


if __name__ == "__main__":
    main()
