def search_player(df, name):
    """
    Search for a product by name in the dataframe.
    """
    product = df[df['product_name'].str.lower() == name.lower()]
    if product.empty:
        return None
    return product.iloc[0]
