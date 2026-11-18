import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.order_manager import OrderManager
from src.copurchase_engine import CoPurchaseEngine
from src.recommendation_engine import RecommendationEngine
from src.evaluation import hit_rate_at_n

ORDERS = [
    {"customer": "C001", "products": ["Laptop", "Mouse", "Keyboard"]},
    {"customer": "C002", "products": ["Laptop", "Mouse"]},
    {"customer": "C003", "products": ["Laptop", "Keyboard", "Monitor"]},
]


def make(orders=ORDERS):
    om = OrderManager(orders)
    return om, RecommendationEngine(om)


class TestCoPurchase(unittest.TestCase):
    def test_pair_counts(self):
        cp = CoPurchaseEngine(ORDERS)
        self.assertEqual(cp.count("Laptop", "Mouse"), 2)
        self.assertEqual(cp.count("Keyboard", "Laptop"), 2)
        self.assertEqual(cp.count("Laptop", "Monitor"), 1)
        self.assertEqual(cp.count("Mouse", "Monitor"), 0)

    def test_duplicates_in_order_counted_once(self):
        cp = CoPurchaseEngine([{"customer": "C1", "products": ["A", "B", "A", "B"]}])
        self.assertEqual(cp.count("A", "B"), 1)
        self.assertEqual(cp.product_counts["A"], 1)

    def test_single_product_order_makes_no_pairs(self):
        cp = CoPurchaseEngine([{"customer": "C1", "products": ["A"]}])
        self.assertEqual(cp.pair_counts, {})

    def test_empty_dataset(self):
        cp = CoPurchaseEngine([])
        self.assertEqual(cp.top_with("A"), [])
        self.assertEqual(cp.best_sellers(), [])


class TestProductRecs(unittest.TestCase):
    def test_top_three(self):
        _, eng = make()
        recs = eng.recommend_for_product("Laptop")
        self.assertEqual([r[0] for r in recs], ["Keyboard", "Mouse", "Monitor"])
        self.assertEqual([r[1] for r in recs], [2, 2, 1])  # tie -> alphabetical

    def test_fewer_than_three(self):
        _, eng = make()
        self.assertEqual([r[0] for r in eng.recommend_for_product("Monitor")],
                         ["Keyboard", "Laptop"])

    def test_unknown_product(self):
        _, eng = make()
        self.assertEqual(eng.recommend_for_product("Nope"), [])

    def test_reason_text(self):
        _, eng = make()
        self.assertIn("2 orders", eng.recommend_for_product("Laptop")[0][2])


class TestCustomerRecs(unittest.TestCase):
    def test_excludes_owned_and_ranks(self):
        om, eng = make()
        recs, mode = eng.recommend_for_customer("C002")  # owns Laptop, Mouse
        names = [r[0] for r in recs]
        self.assertNotIn("Laptop", names)
        self.assertNotIn("Mouse", names)
        self.assertEqual(names[0], "Keyboard")  # 2 (Laptop) + 1 (Mouse) = 3
        self.assertEqual(mode, "personalised")

    def test_customer_owning_nearly_everything(self):
        om, eng = make()
        om.add_order("C9", ["Laptop", "Mouse", "Keyboard"])
        eng.refresh()
        recs, _ = eng.recommend_for_customer("C9")
        self.assertEqual([r[0] for r in recs], ["Monitor"])

    def test_unknown_customer_gets_best_sellers(self):
        _, eng = make()
        recs, mode = eng.recommend_for_customer("NEW")
        self.assertEqual(mode, "bestseller")
        self.assertEqual(recs[0][0], "Laptop")

    def test_best_seller_ranking(self):
        _, eng = make()
        self.assertEqual([r[0] for r in eng.best_sellers(3)],
                         ["Laptop", "Keyboard", "Mouse"])

    def test_empty_dataset(self):
        _, eng = make([])
        self.assertEqual(eng.recommend_for_customer("C1"), ([], "bestseller"))
        self.assertEqual(eng.best_sellers(), [])


class TestSimilarity(unittest.TestCase):
    def test_similar_customer(self):
        _, eng = make()
        other, shared, sim = eng.similar_customer("C001")
        self.assertEqual(other, "C002")
        self.assertEqual(shared, ["Laptop", "Mouse"])

    def test_no_history(self):
        _, eng = make()
        self.assertIsNone(eng.similar_customer("ZZZ"))


class TestOrderManager(unittest.TestCase):
    def test_invalid_orders_rejected(self):
        om = OrderManager()
        self.assertFalse(om.add_order("", ["A"]))
        self.assertFalse(om.add_order("C1", []))
        self.assertFalse(om.add_order("C1", ["  ", ""]))
        self.assertEqual(om.orders, [])

    def test_case_insensitive_lookup(self):
        om, _ = make()
        self.assertEqual(om.find_product("laptop"), "Laptop")
        self.assertEqual(om.find_customer("c001"), "C001")
        self.assertIsNone(om.find_product("xyz"))

    def test_save_and_load(self):
        om, _ = make()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "o.json")
            om.save_json(path)
            om2 = OrderManager()
            self.assertEqual(om2.load_json(path), 3)
            self.assertEqual(om2.orders, om.orders)


class TestEvaluation(unittest.TestCase):
    def test_runs(self):
        _, eng = make()
        hits, trials = hit_rate_at_n(eng)
        self.assertEqual(trials, 3)
        self.assertLessEqual(hits, trials)


if __name__ == "__main__":
    unittest.main()
