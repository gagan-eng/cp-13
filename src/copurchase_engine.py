"""Co-purchase counting: how often do products appear together in an order?"""
from collections import defaultdict
from itertools import combinations

from .order_manager import unique_products


class CoPurchaseEngine:
    def __init__(self, orders):
        self.pair_counts = {}                    # (a, b) with a < b -> orders
        self.product_counts = defaultdict(int)   # product -> orders containing it
        self.neighbors = defaultdict(dict)       # product -> {other: orders together}
        self._build(orders)

    def _build(self, orders):
        for order in orders:
            items = unique_products(order["products"])  # once per order
            for p in items:
                self.product_counts[p] += 1
            for a, b in combinations(items, 2):
                self.pair_counts[(a, b)] = self.pair_counts.get((a, b), 0) + 1
                self.neighbors[a][b] = self.neighbors[a].get(b, 0) + 1
                self.neighbors[b][a] = self.neighbors[b].get(a, 0) + 1

    def count(self, a, b):
        key = (a, b) if a < b else (b, a)
        return self.pair_counts.get(key, 0)

    def sorted_pairs(self):
        """Pairs sorted by count desc, then alphabetically (deterministic)."""
        return sorted(self.pair_counts.items(), key=lambda kv: (-kv[1], kv[0]))

    def top_with(self, product, n=3):
        """Top-n products bought with `product`: [(other, count), ...]."""
        others = self.neighbors.get(product, {})
        return sorted(others.items(), key=lambda kv: (-kv[1], kv[0]))[:n]

    def best_sellers(self, n=3, exclude=()):
        """Products ranked by number of orders they appear in."""
        ex = set(exclude)
        ranked = sorted(self.product_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return [(p, c) for p, c in ranked if p not in ex][:n]
