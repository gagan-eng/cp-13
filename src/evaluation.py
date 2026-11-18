"""Simple leave-one-out hit-rate evaluation of the recommender."""
from .order_manager import unique_products


def hit_rate_at_n(engine, n=3):
    """For each order with 2+ unique products, hide one item and check whether
    it appears in the top-n recommendations made from the remaining items.
    Returns (hits, trials)."""
    hits = trials = 0
    for order in engine.om.orders:
        items = unique_products(order["products"])
        if len(items) < 2:
            continue
        held_out = items[-1]
        basket = items[:-1]
        # Temporarily take this order out of the live counts instead of
        # rebuilding every count from scratch (O(orders) -> O(order size^2)).
        engine.cp.remove_order(order)
        try:
            recs = engine.recommend_for_basket(basket, n)
        finally:
            engine.cp.add_order(order)
        trials += 1
        if held_out in [r[0] for r in recs]:
            hits += 1
    return hits, trials
