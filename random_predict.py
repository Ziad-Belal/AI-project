# random_predict.py
import random
import datetime
from src.predictor import predict_player_value, predict_performance

# categories and brands for realistic products
CATEGORIES = ["Snacks", "Beverages", "Dairy", "Cleaning", "Cosmetics", "Frozen"]
BRANDS = ["BrandA", "BrandB", "BrandC", "BrandX", "BrandY"]
SEASONAL = ["Low", "Medium", "High"]

def make_random_player(season=None):
    """Return a dict representing a fake/random PRODUCT."""
    
    product = {
        "product_id": random.randint(1, 9999),
        "product_name": f"Product {random.randint(100,999)}",
        "category": random.choice(CATEGORIES),
        "brand_name": random.choice(BRANDS),

        "supplier_price": round(random.uniform(5, 80), 2),
        "selling_price": round(random.uniform(10, 140), 2),
        "profit_per_unit": round(random.uniform(1, 60), 2),
        "storage_cost_per_day": round(random.uniform(0.1, 2.5), 2),
        "discount_rate": round(random.uniform(0, 0.5), 2),

        "expiration_days_left": random.randint(0, 100),
        "shelf_life_total_days": random.randint(30, 180),

        "current_stock": random.randint(0, 200),
        "units_sold_last_7_days": random.randint(0, 80),
        "units_sold_last_30_days": random.randint(0, 300),
        "demand_score": random.randint(1, 100),
        "seasonal_demand": random.choice(SEASONAL),

        "supplier_lead_time": random.randint(1, 20),
        "restock_quantity_min": random.randint(10, 50),
        "restock_quantity_max": random.randint(51, 100),

        "expected_units_sold_before_expiration": random.randint(0, 100),
        "expected_revenue": round(random.uniform(100, 12000), 2),
        "expected_profit": round(random.uniform(-500, 5000), 2),

        "should_restock": random.randint(0, 1),
    }

    return product


def pretty_print_player(product):
    print("\n=== PRODUCT INFO ===")
    print(f"ID: {product.get('product_id')}")
    print(f"Name: {product.get('product_name')}")
    print(f"Category: {product.get('category')} | Brand: {product.get('brand_name')}")
    print(f"Selling Price: {product.get('selling_price')} | Profit/Unit: {product.get('profit_per_unit')}")
    print(f"Stock: {product.get('current_stock')} | Sold 7 days: {product.get('units_sold_last_7_days')}")
    print(f"Demand Score: {product.get('demand_score')} | Seasonal: {product.get('seasonal_demand')}")
    print(f"Expected Revenue: {product.get('expected_revenue')}")
    print(f"Should Restock: {product.get('should_restock')}")


def run_once(use_random=True, provided_player=None):
    """
    If use_random=True the script creates a random PRODUCT and predicts.
    """
    if use_random:
        product = make_random_player()
    else:
        if not isinstance(provided_player, dict):
            raise ValueError("If use_random is False, supply provided_player as a dict")
        product = provided_player

    print("\n=== Input Product (Fake) ===")
    pretty_print_player(product)

    try:
        value = predict_player_value(product)
    except Exception as e:
        value = f"ERROR in predict_player_value: {e}"

    try:
        perf = predict_performance(product)
    except Exception as e:
        perf = f"ERROR in predict_performance: {e}"

    print("\n=== Predictions ===")
    print(f"Predicted Value Score: {value}")
    print(f"Predicted Future Performance: {perf}")


if __name__ == "__main__":
    run_once(use_random=True)
