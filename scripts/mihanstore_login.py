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

        # Login page (commonly act=logins)
        page.goto(f"{base}?act=logins", wait_until="domcontentloaded")

        # Try multiple common selectors because this is a PHP partner panel.
        # You may need to adjust once we see the real DOM.
        def fill_any(selectors, value):
            for sel in selectors:
                if page.locator(sel).count() > 0:
                    page.fill(sel, value)
                    return True
            return False

        filled_user = fill_any(
            [
                'input[name="username"]',
                'input[name="user"]',
                'input[name="email"]',
                'input[type="text"]',
            ],
            username,
        )
        filled_pass = fill_any(
            [
                'input[name="password"]',
                'input[name="pass"]',
                'input[type="password"]',
            ],
            password,
        )

        if not filled_user or not filled_pass:
            raise SystemExit("Could not find login fields. Run with headless=False and inspect selectors.")

        # Submit: try button/input submit.
        submitted = False
        for sel in ['button[type="submit"]', 'input[type="submit"]']:
            if page.locator(sel).count() > 0:
                page.click(sel)
                submitted = True
                break
        if not submitted:
            # fallback: press Enter in password field
            page.keyboard.press("Enter")

        page.wait_for_timeout(2000)

        # Save session storage state
        context.storage_state(path=str(state_path))
        browser.close()

    print(f"Saved auth state to: {state_path}")


if __name__ == "__main__":
    main()
