import pandas as pd
import os

def load_and_combine():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory (ve folder)
    ve_dir = os.path.dirname(script_dir)
    
    # CSV paths (relative to ve directory)
    csv1_path = os.path.join(ve_dir, "data", "All_Players.csv")
    csv2_path = os.path.join(ve_dir, "data", "Season.csv")

    # Load CSVs
    df1 = pd.read_csv(csv1_path)
    df2 = pd.read_csv(csv2_path)

    # Combine both CSVs into one DataFrame
    combined_df = pd.concat([df1, df2], ignore_index=True)

    # Remove duplicate players based on the 'Player' column
    combined_df = combined_df.drop_duplicates(subset="Player")

    # Fill missing values with 'Unknown'
    combined_df = combined_df.fillna("Unknown")

    return combined_df
print("suii")