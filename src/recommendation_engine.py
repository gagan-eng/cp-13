"""Recommendation logic: product-based, customer-based, fallback, similarity."""
import heapq

from .copurchase_engine import CoPurchaseEngine


def _orders_word(n):
    return "1 order" if n == 1 else f"{n} orders"


class RecommendationEngine:
    def __init__(self, order_manager):
        self.om = order_manager
        self._rebuild()

    def _rebuild(self):
        self.cp = CoPurchaseEngine(self.om.orders)
        self._synced = len(self.om.orders)
        self._epoch = self.om.epoch

    def refresh(self):
        """Bring counts up to date after orders change. Orders appended since
        the last sync are folded in incrementally; if the order list was
        replaced (e.g. load_json) everything is rebuilt."""
        if self._epoch != self.om.epoch or len(self.om.orders) < self._synced:
            self._rebuild()
            return
        for order in self.om.orders[self._synced:]:
            self.cp.add_order(order)
        self._synced = len(self.om.orders)

    # ---- 3. product-based ----------------------------------------------
    def recommend_for_product(self, product, n=3):
        """[(product, co_count, reason)] - top products bought with `product`."""
        return [
            (other, cnt, f"Bought with {product} in {_orders_word(cnt)}.")
            for other, cnt in self.cp.top_with(product, n)
        ]

    # ---- 4. customer-based ---------------------------------------------
    @staticmethod
    def _basket_scores(basket, cp):
        """Aggregate co-purchase counts from the basket; skip owned items.
        Returns {candidate: (score, {basket_item: count})}."""
        scores = {}
        for owned in basket:
            for other, cnt in cp.neighbors.get(owned, {}).items():
                if other in basket:
                    continue
                score, src = scores.get(other, (0, {}))
                src[owned] = cnt
                scores[other] = (score + cnt, src)
        return scores

    def _rank_basket(self, basket, cp, n):
        scores = self._basket_scores(basket, cp)
        ranked = heapq.nsmallest(n, scores.items(),
                                 key=lambda kv: (-kv[1][0], kv[0]))
        results = []
        for product, (score, src) in ranked:
            parts = ", ".join(
                f"{p} ({_orders_word(c)})"
                for p, c in sorted(src.items(), key=lambda kv: (-kv[1], kv[0]))
            )
            results.append((product, score, f"Bought together with {parts}."))
        return results

    def recommend_for_customer(self, customer, n=3):
        """Returns (results, mode) where mode is 'personalised', 'mixed'
        or 'bestseller'. results = [(product, score, reason)]."""
        basket = self.om.history(customer)
        if not basket:
            return self.best_sellers(n), "bestseller"

        results = self._rank_basket(basket, self.cp, n)
        mode = "personalised"
        if len(results) < n:  # top up with popular items not yet owned
            have = basket | {r[0] for r in results}
            for p, c in self.cp.best_sellers(n, exclude=have):
                if len(results) >= n:
                    break
                results.append((p, c, f"Best seller: appears in {_orders_word(c)}."))
                mode = "mixed"
        return results, mode

    # ---- 5. best-seller fallback ----------------------------------------
    def best_sellers(self, n=3):
        return [
            (p, c, f"Best seller: appears in {_orders_word(c)}.")
            for p, c in self.cp.best_sellers(n)
        ]

    # ---- stretch: similar customer --------------------------------------
    def similar_customer(self, customer):
        """Most similar other customer by Jaccard similarity of purchases.
        Returns (customer, shared_products, similarity) or None."""
        mine = self.om.history(customer)
        if not mine:
            return None
        best = None
        # only customers sharing at least one product can have similarity > 0
        candidates = set()
        for product in mine:
            candidates |= self.om.buyers(product)
        candidates.discard(customer)
        for other in candidates:
            theirs = self.om.history(other)
            shared = mine & theirs
            if not shared:
                continue
            sim = len(shared) / len(mine | theirs)
            key = (sim, len(shared))
            if best is None or key > best[0] or (key == best[0] and other < best[1]):
                best = (key, other, shared, sim)
        if best is None:
            return None
        return best[1], sorted(best[2]), best[3]

    # ---- evaluation helper ----------------------------------------------
    def recommend_for_basket(self, basket, n=3):
        """Recommend for an ad-hoc basket using the current counts."""
        return self._rank_basket(set(basket), self.cp, n)

    def recommend_for_basket_with(self, basket, orders, n=3):
        """Recommend for a basket using counts built from `orders`."""
        cp = CoPurchaseEngine(orders)
        return self._rank_basket(set(basket), cp, n)
