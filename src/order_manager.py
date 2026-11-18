"""Order storage and persistence for BuyNext."""
import json
import os


def clean_products(products):
    """Strip whitespace and drop empty / non-string entries (keeps duplicates)."""
    return [p.strip() for p in products if isinstance(p, str) and p.strip()]


def unique_products(products):
    """Unique products of one order (each product counted once per order)."""
    return sorted(set(clean_products(products)))


class OrderManager:
    """Holds orders: [{"customer": "C001", "products": [...]}, ...]."""

    def __init__(self, orders=None):
        self.orders = []
        for o in orders or []:
            self.add_order(o.get("customer"), o.get("products", []))

    # ---- mutation -------------------------------------------------------
    def add_order(self, customer, products):
        """Add an order. Returns True on success, False if invalid/empty."""
        if not isinstance(customer, str) or not customer.strip():
            return False
        products = clean_products(products or [])
        if not products:
            return False
        self.orders.append({"customer": customer.strip(), "products": products})
        return True

    # ---- queries --------------------------------------------------------
    def customers(self):
        return sorted({o["customer"] for o in self.orders})

    def all_products(self):
        items = set()
        for o in self.orders:
            items.update(o["products"])
        return sorted(items)

    def find_customer(self, name):
        """Case-insensitive customer lookup. Returns canonical id or None."""
        if not name:
            return None
        key = name.strip().lower()
        for c in self.customers():
            if c.lower() == key:
                return c
        return None

    def find_product(self, name):
        """Case-insensitive product lookup. Returns canonical name or None."""
        if not name:
            return None
        key = name.strip().lower()
        for p in self.all_products():
            if p.lower() == key:
                return p
        return None

    def history(self, customer):
        """Set of all distinct products a customer has purchased."""
        items = set()
        for o in self.orders:
            if o["customer"] == customer:
                items.update(o["products"])
        return items

    # ---- persistence ----------------------------------------------------
    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.orders = []
        for o in data:
            self.add_order(o.get("customer"), o.get("products", []))
        return len(self.orders)

    def save_json(self, path):
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.orders, f, indent=2)
