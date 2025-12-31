"""Sync vendor products into local catalog."""

from __future__ import annotations

from typing import List

from control.catalog.models import Product
from control.catalog.store import catalog
from control.vendors.registry import VENDORS


async def sync_all_vendors() -> dict:
    results = {}
    for name, vendor in VENDORS.items():
        products = await vendor.fetch_products()
        results[name] = len(products)
        for vp in products:
            sku = f"{vp.vendor}:{vp.sku}"
            catalog.upsert(
                Product(
                    sku=sku,
                    title=vp.title,
                    price_toman=vp.price_toman,
                    description="",
                    image_url=vp.image_url,
                    buy_url=vp.url,
                    category=vp.category,
                )
            )
    return results
