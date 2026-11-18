"""Order storage and persistence for BuyNext."""
import json
import os


def clean_products(products):
    """Strip whitespace and drop empty / non-string entries (keeps duplicates)."""
    return [p.strip() for p in products if isinstance(p, str) and p.strip()]


def unique_products(products):
    """Unique products of one order (each product counted once per order)."""
    return sorted(set(clean_products(products)))


def _keep_first(mapping, canonical):
    """Case-insensitive key -> canonical spelling; on a clash the
    alphabetically first spelling wins (same rule as a sorted scan)."""
    key = canonical.lower()
    if key not in mapping or canonical < mapping[key]:
        mapping[key] = canonical


class OrderManager:
    """Holds orders: [{"customer": "C001", "products": [...]}, ...]."""

    def __init__(self, orders=None):
        self._reset()
        for o in orders or []:
            self.add_order(o.get("customer"), o.get("products", []))

    def _reset(self):
        """Clear orders and the lookup indexes built from them."""
        self.orders = []
        self.epoch = getattr(self, "epoch", 0) + 1  # bumps when orders are replaced
        self._history = {}   # customer -> set of products they bought
        self._buyers = {}    # product  -> set of customers who bought it
        self._cust_lower = {}  # lower-case id -> canonical customer id
        self._prod_lower = {}  # lower-case name -> canonical product name

    # ---- mutation -------------------------------------------------------
    def add_order(self, customer, products):
        """Add an order. Returns True on success, False if invalid/empty."""
        if not isinstance(customer, str) or not customer.strip():
            return False
        products = clean_products(products or [])
        if not products:
            return False
        customer = customer.strip()
        self.orders.append({"customer": customer, "products": products})
        self._index(customer, products)
        return True

    def _index(self, customer, products):
        """Update lookup indexes for one new order (O(products in order))."""
        self._history.setdefault(customer, set()).update(products)
        _keep_first(self._cust_lower, customer)
        for p in products:
            self._buyers.setdefault(p, set()).add(customer)
            _keep_first(self._prod_lower, p)

    # ---- queries (all index-backed; no scan over orders) ----------------
    def customers(self):
        return sorted(self._history)

    def all_products(self):
        return sorted(self._buyers)

    def find_customer(self, name):
        """Case-insensitive customer lookup. Returns canonical id or None."""
        if not name:
            return None
        return self._cust_lower.get(name.strip().lower())

    def find_product(self, name):
        """Case-insensitive product lookup. Returns canonical name or None."""
        if not name:
            return None
        return self._prod_lower.get(name.strip().lower())

    def history(self, customer):
        """Set of all distinct products a customer has purchased.
        Treat the result as read-only."""
        return self._history.get(customer, set())

    def buyers(self, product):
        """Set of customers who bought `product`. Treat as read-only."""
        return self._buyers.get(product, set())

    # ---- persistence ----------------------------------------------------
    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._reset()
        for o in data:
            self.add_order(o.get("customer"), o.get("products", []))
        return len(self.orders)

    def save_json(self, path):
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.orders, f, indent=2)
