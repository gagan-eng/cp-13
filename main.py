#!/usr/bin/env python3
"""BuyNext - Co-Purchase Product Recommendation Engine (console app)."""
import os
import sys

from src.order_manager import OrderManager
from src.recommendation_engine import RecommendationEngine
from src.evaluation import hit_rate_at_n

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "sample_orders.json")

MENU = """
==================== BuyNext ====================
 1. View all orders
 2. Add a new order
 3. Show co-purchase counts
 4. Recommend by product   ("Customers who bought X also bought")
 5. Recommend for customer
 6. Show best sellers
 7. Find similar customer
 8. Evaluate recommender (hit rate @3)
 9. Save orders to file
 0. Exit
=================================================="""


def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        print()
        return "0"


def print_recs(recs, with_reason=True):
    if not recs:
        print("  (no recommendations available)")
        return
    for i, (product, score, reason) in enumerate(recs, 1):
        print(f"  {i}. {product}")
        if with_reason:
            print(f"     Reason: {reason}")


def view_orders(om):
    if not om.orders:
        print("No orders stored.")
        return
    for i, o in enumerate(om.orders, 1):
        print(f"  #{i:<3} {o['customer']:<6} {', '.join(o['products'])}")
    print(f"Total: {len(om.orders)} orders, {len(om.customers())} customers, "
          f"{len(om.all_products())} products")


def add_order(om, eng):
    cust = ask("Customer ID (e.g. C010): ")
    raw = ask("Products (comma separated): ")
    products = [p for p in raw.split(",")]
    # re-use existing capitalisation where the product is already known
    products = [om.find_product(p) or p.strip() for p in products]
    if om.add_order(cust, products):
        eng.refresh()
        print("Order added.")
    else:
        print("Invalid order: need a customer ID and at least one product.")


def show_counts(eng):
    pairs = eng.cp.sorted_pairs()
    if not pairs:
        print("No product pairs yet (need orders with 2+ products).")
        return
    for (a, b), c in pairs:
        print(f"  {a} + {b}: {c} order{'s' if c != 1 else ''}")


def by_product(om, eng):
    print("Known products:", ", ".join(om.all_products()) or "(none)")
    name = ask("Product name: ")
    product = om.find_product(name)
    if not product:
        print(f"Unknown product: '{name}'.")
        return
    recs = eng.recommend_for_product(product)
    print(f"\nCustomers who bought {product} also bought:")
    print_recs(recs)


def for_customer(om, eng):
    print("Known customers:", ", ".join(om.customers()) or "(none)")
    name = ask("Customer ID (new IDs get best sellers): ")
    if not name:
        print("No customer entered.")
        return
    cust = om.find_customer(name) or name
    recs, mode = eng.recommend_for_customer(cust)
    if mode == "bestseller":
        print(f"\n{cust} has no purchase history -> showing best sellers "
              f"(not personalised):")
    else:
        owned = ", ".join(sorted(om.history(cust)))
        print(f"\n{cust} has purchased: {owned}")
        print("Recommended for you:" + (" (topped up with best sellers)"
                                        if mode == "mixed" else ""))
    print_recs(recs)


def best_sellers(eng):
    print("Best sellers (by number of orders):")
    print_recs(eng.best_sellers(5))


def similar(om, eng):
    print("Known customers:", ", ".join(om.customers()) or "(none)")
    cust = om.find_customer(ask("Customer ID: "))
    if not cust:
        print("Unknown customer.")
        return
    res = eng.similar_customer(cust)
    if not res:
        print("No similar customer found.")
        return
    other, shared, sim = res
    print(f"Most similar to {cust}: {other} (similarity {sim:.0%})")
    print(f"  Shared purchases: {', '.join(shared)}")


def evaluate(eng):
    hits, trials = hit_rate_at_n(eng, 3)
    if trials == 0:
        print("Not enough data (need orders with 2+ products).")
    else:
        print(f"Hit rate @3: {hits}/{trials} = {hits / trials:.0%}")


def save(om):
    path = ask(f"Save path [{DATA_FILE}]: ") or DATA_FILE
    om.save_json(path)
    print(f"Saved {len(om.orders)} orders to {path}")


def main():
    om = OrderManager()
    if os.path.exists(DATA_FILE):
        try:
            n = om.load_json(DATA_FILE)
            print(f"Loaded {n} orders from {os.path.relpath(DATA_FILE, BASE)}")
        except (ValueError, OSError) as e:
            print(f"Could not load sample data ({e}); starting empty.")
    else:
        print("No sample data found; starting with an empty store.")
    eng = RecommendationEngine(om)

    actions = {
        "1": lambda: view_orders(om),
        "2": lambda: add_order(om, eng),
        "3": lambda: show_counts(eng),
        "4": lambda: by_product(om, eng),
        "5": lambda: for_customer(om, eng),
        "6": lambda: best_sellers(eng),
        "7": lambda: similar(om, eng),
        "8": lambda: evaluate(eng),
        "9": lambda: save(om),
    }
    while True:
        print(MENU)
        choice = ask("Choose an option: ")
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action:
            print()
            action()
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
