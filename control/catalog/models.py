"""Product catalog models.

Simple in-memory store for now; can be swapped with DB later.
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Product:
    sku: str
    title: str
    price_toman: int
    description: str = ""
    image_url: Optional[str] = None
    buy_url: Optional[str] = None
    category: str = "general"

    def to_dict(self):
        return asdict(self)
