"""Affiliate vendor connector interface + data model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, List


@dataclass
class VendorProduct:
    vendor: str
    sku: str
    title: str
    price_toman: int
    url: str
    image_url: Optional[str] = None
    category: str = "general"


class AffiliateVendor(Protocol):
    name: str

    async def fetch_products(self) -> List[VendorProduct]:
        ...
