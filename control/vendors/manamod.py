"""Manamod vendor connector (scrape based).

NOTE: selectors must be adjusted based on the real site.
"""

from __future__ import annotations

from typing import List

from playwright.async_api import Page

from control.vendors.base import VendorProduct
from control.connectors.playwright_connector import PWConfig, launch_persistent


class ManamodVendor:
    name = "manamod"

    def __init__(self, base_url: str = "https://manamod.net/partner"):
        self.base_url = base_url

    async def fetch_products(self) -> List[VendorProduct]:
        pw, ctx = await launch_persistent(PWConfig(user_data_dir="./data/playwright/manamod", headless=True))
        try:
            page: Page = await ctx.new_page()
            await page.goto(self.base_url, wait_until="domcontentloaded")

            # TODO: replace selectors
            items = []
            cards = await page.query_selector_all("[data-product-card]")
            for c in cards:
                title = (await c.query_selector(".title")).inner_text()
                price_txt = (await c.query_selector(".price")).inner_text()
                url = await (await c.query_selector("a")).get_attribute("href")

                price = int("".join(ch for ch in price_txt if ch.isdigit()) or "0")
                sku = str(hash(title))
                items.append(VendorProduct(vendor=self.name, sku=sku, title=title, price_toman=price, url=url))
            return items
        finally:
            await ctx.close()
            await pw.stop()
