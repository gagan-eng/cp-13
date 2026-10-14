# BuyNext — Co-Purchase Product Recommendation Engine

**Project ID:** CP-013  
**Domain:** E-Commerce and Retail  
**Level:** Advanced

## Overview

BuyNext is a Python-based product recommendation engine that implements the **"Customers who bought this also bought"** feature for an online store.

The system analyses customer orders to calculate how frequently products are purchased together. It uses co-purchase counts to recommend relevant products, suggests items a customer has not purchased, and recommends overall best-selling products to customers with no purchase history.

The project implements recommendation logic using fundamental programming concepts and data structures without requiring a machine-learning platform.

## Objectives

- Store customer orders containing multiple products.
- Calculate co-purchase frequencies for product pairs.
- Recommend the top three products bought most often with a selected product.
- Recommend three products a customer has not purchased.
- Handle new customers using overall best-selling products.
- Explain recommendations using purchase-frequency information.

## Core Features

All five core features are compulsory.

### 1. Order Management

Store orders containing a customer identifier and a list of products purchased together.

Example:

```python
orders = [
    {"customer": "C001", "products": ["Laptop", "Mouse", "Keyboard"]},
    {"customer": "C002", "products": ["Laptop", "Mouse"]},
    {"customer": "C003", "products": ["Laptop", "Keyboard", "Monitor"]}
]
```

### 2. Co-Purchase Counting

Calculate how many orders contain each pair of products. Each product pair should be counted once per order, even if the same product appears multiple times in the raw order data.

Example output:

```text
Laptop + Mouse: 2 orders
Laptop + Keyboard: 2 orders
Laptop + Monitor: 1 order
```

### 3. Product-Based Recommendations

Given a product, display the top three products most frequently purchased alongside it, ranked by co-purchase count.

Example:

```text
Customers who bought Laptop also bought:
1. Mouse
2. Keyboard
3. Monitor
```

The actual ranking depends on the stored orders. If fewer than three eligible products exist, return the available recommendations.

### 4. Customer-Based Recommendations

Recommend three products the customer has not previously purchased, using the co-purchase relationships associated with their purchase history.

The system should aggregate relevant co-purchase counts, exclude products already purchased, and rank the remaining products by recommendation score.

### 5. Best-Seller Fallback

For customers with no purchase history, recommend products based on overall popularity across the order dataset.

Products should be ranked by the number of orders in which they appear, rather than being treated as personalised recommendations.

## Optional Stretch Features

These features can be implemented after all five compulsory features are complete.

### Similar Customer Identification

Find the customer whose purchase history most closely matches a given customer's history using shared purchases.

### Recommendation Explanations

Explain why a product was recommended by showing its co-purchase count.

Example:

```text
Recommended: Mouse
Reason: Bought with Laptop in 12 orders.
```

## Technology Stack

- **Language:** Python
- **Core Concepts:** Dictionaries, sets, lists, loops, functions and sorting
- **Data Storage:** Python data structures initially; JSON or SQLite can be added if required
- **Testing:** Python `unittest` or `pytest`
- **Version Control:** Git and GitHub

No machine-learning framework or external ML platform is required for the compulsory features.

## How It Works

1. **Store Orders:** Record each customer's order and purchased products.
2. **Process Transactions:** Extract unique products from each order.
3. **Build Co-Purchase Counts:** Count each unordered product pair at most once per order.
4. **Generate Product Recommendations:** Rank products by their co-purchase counts with the selected product.
5. **Generate Customer Recommendations:** Aggregate co-purchase counts from the customer's purchase history and exclude previously purchased products.
6. **Handle New Customers:** Recommend the overall best-selling products when purchase history is unavailable.
7. **Explain Recommendations:** Optionally display the purchase relationships behind each suggestion.

## Project Structure

```text
BuyNext/
├── data/
│   └── sample_orders.json
├── src/
│   ├── order_manager.py
│   ├── copurchase_engine.py
│   ├── recommendation_engine.py
│   └── evaluation.py
├── tests/
│   └── test_recommendations.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

This is a suggested structure. You can simplify or modify it to suit your implementation.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd BuyNext
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

The core recommendation engine can run using Python's standard library, so external dependencies are optional.

If your project uses only the standard library, no additional installation is required.

### 4. Run the Project

```bash
python main.py
```

## Testing and Validation

The implementation should be tested against the following scenarios:

- Orders containing two or more products.
- Product pairs appearing across multiple orders.
- Repeated products within a single raw order.
- Products with fewer than three co-purchased alternatives.
- Customers with an empty purchase history.
- Customers who have already purchased most available products.
- Ties between products with equal recommendation counts.
- Empty order datasets and unknown customer or product identifiers.

## Expected Outcomes

- Accurate co-purchase counts for product pairs.
- Top-three recommendations for a selected product.
- Personalised product suggestions based on purchase history.
- Best-seller recommendations for customers with no history.
- Optional explanations for recommended products.

## Future Enhancements

- Add a Streamlit dashboard for interactive recommendations.
- Store orders and product information in SQLite or PostgreSQL.
- Build an API for integrating recommendations into an online store.
- Add customer similarity analysis.
- Add configurable recommendation rules and tie-breaking strategies.
- Explore collaborative filtering or machine-learning methods as optional future extensions.

## Project Information

- **Name:** BuyNext
- **Project ID:** CP-013
- **Domain:** E-Commerce and Retail
- **Level:** Advanced
- **Category:** Recommendation Systems and Data Mining

---

BuyNext demonstrates how useful product recommendations can be generated from transaction history using efficient data structures and transparent recommendation logic, without requiring a machine-learning platform.