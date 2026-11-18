# BuyNext — Co-Purchase Product Recommendation Engine (CP-013)

A console-based Python app implementing "Customers who bought this also bought".
Pure standard library — no ML framework or external packages needed (Python 3.8+).

## Run
```
python main.py
```
Menu options: view/add orders, co-purchase counts, recommend by product,
recommend for customer, best sellers, similar customer, evaluation, save.

## Test
```
python -m unittest discover -s tests -v
```

## How it works
- Each order's products are de-duplicated, so a pair counts once per order.
- **Product recs:** top 3 products by co-purchase count with the chosen product.
- **Customer recs:** sums co-purchase counts from everything the customer owns,
  excludes owned products, returns the top 3 (topped up with best sellers if
  fewer than 3 candidates exist).
- **New customers:** best sellers, ranked by number of orders containing the product.
- **Ties:** broken alphabetically, so results are deterministic.
- **Explanations:** every recommendation shows its supporting order counts.
- **Stretch:** similar-customer search (Jaccard similarity) and a hit-rate@3 evaluation.

## Structure
```
BuyNext/
├── data/sample_orders.json
├── src/order_manager.py, copurchase_engine.py, recommendation_engine.py, evaluation.py
├── tests/test_recommendations.py
├── main.py
├── requirements.txt
└── README.md
```
