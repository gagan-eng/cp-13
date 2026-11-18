"""Simple leave-one-out hit-rate evaluation of the recommender."""
from .order_manager import unique_products


def hit_rate_at_n(engine, n=3):
    """For each order with 2+ unique products, hide one item and check whether
    it appears in the top-n recommendations made from the remaining items.
    Returns (hits, trials)."""
    orders = engine.om.orders
    hits = trials = 0
    for i, order in enumerate(orders):
        items = unique_products(order["products"])
        if len(items) < 2:
            continue
        held_out = items[-1]
        basket = items[:-1]
        others = orders[:i] + orders[i + 1:]
        recs = engine.recommend_for_basket_with(basket, others, n)
        trials += 1
        if held_out in [r[0] for r in recs]:
            hits += 1
    return hits, trials
