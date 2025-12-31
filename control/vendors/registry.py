"""Vendor registry."""

from control.vendors.manamod import ManamodVendor
from control.vendors.mihanstore import MihanStoreVendor
from control.vendors.memarket import MemarketVendor

VENDORS = {
    "manamod": ManamodVendor(),
    "mihanstore": MihanStoreVendor(),
    "memarket": MemarketVendor(),
}
