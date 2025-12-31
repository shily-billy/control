"""In-memory catalog store."""

from typing import Dict, List, Optional
from control.catalog.models import Product


class CatalogStore:
    def __init__(self):
        self._items: Dict[str, Product] = {}

    def upsert(self, p: Product):
        self._items[p.sku] = p

    def get(self, sku: str) -> Optional[Product]:
        return self._items.get(sku)

    def list(self, category: Optional[str] = None) -> List[Product]:
        items = list(self._items.values())
        if category:
            items = [p for p in items if p.category == category]
        return sorted(items, key=lambda p: p.sku)


catalog = CatalogStore()

# Demo products (replace later with DB/admin panel)
catalog.upsert(Product(sku="P001", title="نمونه محصول ۱", price_toman=150000, description="توضیح کوتاه", category="general"))
catalog.upsert(Product(sku="P002", title="نمونه محصول ۲", price_toman=245000, description="توضیح کوتاه", category="general"))
