"""Co-purchase counting: how often do products appear together in an order?"""
from collections import defaultdict
import heapq
from itertools import combinations

from .order_manager import unique_products


def _bump(counts, key, delta):
    new = counts.get(key, 0) + delta
    if new > 0:
        counts[key] = new
    else:
        counts.pop(key, None)


class CoPurchaseEngine:
    def __init__(self, orders):
        self.pair_counts = {}                    # (a, b) with a < b -> orders
        self.product_counts = defaultdict(int)   # product -> orders containing it
        self.neighbors = defaultdict(dict)       # product -> {other: orders together}
        self._build(orders)

    def _build(self, orders):
        for order in orders:
            self.add_order(order)

    def add_order(self, order):
        """Add one order's contribution to all counts."""
        self._apply(unique_products(order["products"]), +1)

    def remove_order(self, order):
        """Undo add_order for an order that was previously added."""
        self._apply(unique_products(order["products"]), -1)

    def _apply(self, items, delta):
        """Shift counts by +1/-1 for a de-duplicated item list; zeroed
        entries are deleted so they never show up in rankings."""
        for p in items:
            _bump(self.product_counts, p, delta)
        for a, b in combinations(items, 2):
            _bump(self.pair_counts, (a, b), delta)
            _bump(self.neighbors[a], b, delta)
            _bump(self.neighbors[b], a, delta)

    def count(self, a, b):
        key = (a, b) if a < b else (b, a)
        return self.pair_counts.get(key, 0)

    def sorted_pairs(self):
        """Pairs sorted by count desc, then alphabetically (deterministic)."""
        return sorted(self.pair_counts.items(), key=lambda kv: (-kv[1], kv[0]))

    def top_with(self, product, n=3):
        """Top-n products bought with `product`: [(other, count), ...]."""
        others = self.neighbors.get(product, {})
        return heapq.nsmallest(n, others.items(), key=lambda kv: (-kv[1], kv[0]))

    def best_sellers(self, n=3, exclude=()):
        """Products ranked by number of orders they appear in."""
        ex = set(exclude)
        items = ((p, c) for p, c in self.product_counts.items() if p not in ex)
        return heapq.nsmallest(n, items, key=lambda kv: (-kv[1], kv[0]))
