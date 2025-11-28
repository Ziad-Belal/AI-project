def is_active(product_row):
    """
    Check if a product is 'active' (has sales in the last 7 days).
    Returns True if units_sold_last_7_days > 0, else False.
    """
    try:
        return int(product_row.get('units_sold_last_7_days', 0)) > 0
    except ValueError:
        # If value is missing or invalid, consider product inactive
        return False
