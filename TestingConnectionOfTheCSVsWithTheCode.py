import pandas as pd

df = pd.read_csv("data/products_dataset.csv")
# Show column names, types, and missing values
print(df.info())

# Check basic statistics
print(df.describe())
