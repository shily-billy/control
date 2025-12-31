"""Manamod vendor connector (scrape based) - selectors derived from /products/list HTML.

Extracts products from the table in:
- https://manamod.net/products/list

Supports pagination via ?page=N.

Expected columns (per row) based on the provided HTML:
1) Row index
2) Product ID
3) Product title
4) Price (e.g. 598,000)
5) Commission (e.g. 67,000)
6) Image (img src)
7) Cover link (https://manamod.net/products/cover/<id>)

Notes:
- This endpoint likely requires authentication.
- Persistent context is used so login cookies/session can be retained.
"""

from __future__ import annotations

from typing import List

from playwright.async_api import Page

from control.connectors.playwright_connector import PWConfig, launch_persistent
from control.vendors.base import VendorProduct


class ManamodVendor:
    name = "manamod"

    def __init__(self, base_url: str = "https://manamod.net/products/list", max_pages: int = 2):
        self.base_url = base_url
        self.max_pages = max_pages

    @staticmethod
    def _to_int(text: str) -> int:
        digits = "".join(ch for ch in (text or "") if ch.isdigit())
        return int(digits or "0")

    async def _parse_table(self, page: Page) -> List[VendorProduct]:
        items: List[VendorProduct] = []

        table = await page.query_selector("table.table")
        if not table:
            return items

        rows = await table.query_selector_all("tr")
        for r in rows:
            tds = await r.query_selector_all("td")
            if len(tds) < 7:
                continue

            prod_id = (await tds[1].inner_text()).strip()
            title = (await tds[2].inner_text()).strip()
            price_txt = (await tds[3].inner_text()).strip()

            img = await tds[5].query_selector("img")
            img_src = (await img.get_attribute("src")) if img else None

            cover_a = await tds[6].query_selector("a")
            cover_url = (await cover_a.get_attribute("href")) if cover_a else None

            if cover_url and cover_url.startswith("/"):
                cover_url = f"https://manamod.net{cover_url}"
            if img_src and img_src.startswith("/"):
                img_src = f"https://manamod.net{img_src}"

            url = cover_url or f"https://manamod.net/products/cover/{prod_id}"

            items.append(
                VendorProduct(
                    vendor=self.name,
                    sku=prod_id,
                    title=title,
                    price_toman=self._to_int(price_txt),
                    url=url,
                    image_url=img_src,
                    category="general",
                )
            )

        return items

    async def fetch_products(self) -> List[VendorProduct]:
        pw, ctx = await launch_persistent(PWConfig(user_data_dir="./data/playwright/manamod", headless=True))
        try:
            page: Page = await ctx.new_page()

            all_items: List[VendorProduct] = []
            for p in range(1, self.max_pages + 1):
                url = self.base_url if p == 1 else f"{self.base_url}?page={p}"
                await page.goto(url, wait_until="domcontentloaded")

                items = await self._parse_table(page)
                if not items:
                    break

                all_items.extend(items)

            return all_items
        finally:
            await ctx.close()
            await pw.stop()
