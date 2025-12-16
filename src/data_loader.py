import pandas as pd
import os

def load_and_combine():
    """Load and combine CSV files"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ve_dir = os.path.dirname(script_dir)
    
    csv1_path = os.path.join(ve_dir, "data", "All_Players.csv")
    csv2_path = os.path.join(ve_dir, "data", "Season.csv")
    
    df1 = pd.read_csv(csv1_path)
    df2 = pd.read_csv(csv2_path)
    combined_df = pd.concat([df1, df2], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset="Player")
    combined_df = combined_df.fillna("Unknown")
    
    return combined_df
