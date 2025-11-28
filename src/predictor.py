def predict_player_value(product_row):
    """
    Simple estimation model for product value.
    Uses selling_price, profit_per_unit, and demand_score.
    """

    try:
        price = float(product_row.get("selling_price", 0))
    except:
        price = 0

    try:
        profit = float(product_row.get("profit_per_unit", 0))
    except:
        profit = 0

    try:
        demand = float(product_row.get("demand_score", 0))
    except:
        demand = 0

    # Base value score
    value_score = price + (profit * 2) + (demand * 1.5)

    return round(value_score, 2)


def predict_performance(product_row):
    """
    Predict future performance based on sales and expected revenue.
    """

    try:
        sold_7 = float(product_row.get("units_sold_last_7_days", 0))
    except:
        sold_7 = 0

    try:
        sold_30 = float(product_row.get("units_sold_last_30_days", 0))
    except:
        sold_30 = 0

    try:
        expected_rev = float(product_row.get("expected_revenue", 0))
    except:
        expected_rev = 0

    # Basic prediction logic
    predicted_sales = sold_30 * 1.10  # +10%
    predicted_revenue = expected_rev * 1.05  # +5%

    return {
        "predicted_sales": round(predicted_sales, 2),
        "predicted_revenue": round(predicted_revenue, 2)
    }


# ======================================================
#               RUNNING THE TOOL MANUALLY
# ======================================================
if __name__ == "__main__":
    print("=== Enter Product Stats ===")

    name = input("Product Name: ")
    price = input("Selling Price: ")
    profit = input("Profit per Unit: ")
    demand = input("Demand Score: ")
    sold7 = input("Units Sold Last 7 Days: ")
    sold30 = input("Units Sold Last 30 Days: ")
    expected_rev = input("Expected Revenue: ")

    # Fake CSV Row
    product_row = {
        "product_name": name,
        "selling_price": price,
        "profit_per_unit": profit,
        "demand_score": demand,
        "units_sold_last_7_days": sold7,
        "units_sold_last_30_days": sold30,
        "expected_revenue": expected_rev
    }

    # Predictions
    value = predict_player_value(product_row)
    perf = predict_performance(product_row)

    print("\n=== Product Prediction Results ===")
    print(f"Product: {name}")
    print(f"Estimated Product Value Score: {value}")
    print(f"Predicted Sales (Next Period): {perf['predicted_sales']}")
    print(f"Predicted Revenue: {perf['predicted_revenue']}")
