import pandas as pd

def load_and_combine():
    # CSV paths
    csv1_path = "data/products_dataset.csv"
  

    # Load CSVs
    df1 = pd.read_csv(csv1_path)

    # Combine both CSVs into one DataFrame
    combined_df = pd.concat([df1], ignore_index=True)

    # Remove duplicate players based on the 'Player' column
    combined_df = combined_df.drop_duplicates(subset="Player")

    # Fill missing values with 'Unknown'
    combined_df = combined_df.fillna("Unknown")

    return combined_df
print("suii")