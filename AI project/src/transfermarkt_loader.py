"""
Loader for Transfermarkt transfer data
Integrates real market value data into the training pipeline
"""
import pandas as pd
import os
import glob
from difflib import SequenceMatcher

def normalize_name(name):
    """Normalize player name for matching"""
    if pd.isna(name) or name == '':
        return ''
    # Remove accents, convert to lowercase, strip whitespace
    name = str(name).lower().strip()
    # Remove common suffixes
    name = name.replace(' jr.', '').replace(' sr.', '').replace(' ii', '').replace(' iii', '')
    return name

def fuzzy_match_name(name1, name2, threshold=0.85):
    """Check if two names match using fuzzy matching"""
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    if not norm1 or not norm2:
        return False
    # Exact match
    if norm1 == norm2:
        return True
    # Fuzzy match
    ratio = SequenceMatcher(None, norm1, norm2).ratio()
    return ratio >= threshold

def load_transfermarkt_data(base_path=None):
    """
    Load all transfermarkt CSV files from all leagues
    
    Args:
        base_path: Path to transfermarkt-data-master directory
                   If None, assumes it's in the parent directory
    
    Returns:
        DataFrame with all transfermarkt data
    """
    if base_path is None:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Get the parent directory
        ve_dir = os.path.dirname(script_dir)
        # Go up one more level to reach the football project root
        project_root = os.path.dirname(ve_dir)
        base_path = os.path.join(project_root, "transfermarkt-data-master")
    
    if not os.path.exists(base_path):
        print(f"Warning: Transfermarkt data directory not found at {base_path}")
        return pd.DataFrame()
    
    # List of leagues to process
    leagues = [
        'premier_league', 'laliga', 'bundesliga', 'serie_a',
        'ligue_1', 'eredivisie', 'super_lig', 'saudi_pro_league'
    ]
    
    all_data = []
    
    for league in leagues:
        league_path = os.path.join(base_path, league)
        if not os.path.exists(league_path):
            continue
        
        # Find all CSV files in the league directory
        csv_files = glob.glob(os.path.join(league_path, "*.csv"))
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                if not df.empty:
                    all_data.append(df)
            except Exception as e:
                print(f"Warning: Could not load {csv_file}: {e}")
                continue
    
    if not all_data:
        print("Warning: No transfermarkt data found")
        return pd.DataFrame()
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Filter for valid market values (only 'in' transfers, non-loans, with market_value)
    # We use 'in' transfers to get the market value at the time of transfer
    valid_df = combined_df[
        (combined_df['movement'] == 'in') &
        (combined_df['is_loan'] == 0) &
        (combined_df['market_value'].notna()) &
        (combined_df['market_value'] > 0) &
        (combined_df['age'].notna()) &
        (combined_df['age'] >= 16) &
        (combined_df['age'] <= 50)
    ].copy()
    
    # Convert market_value from euros to millions
    valid_df['market_value_millions'] = valid_df['market_value'] / 1_000_000
    
    # Group by player_name and age to get average market value per player-age combination
    # This helps handle multiple transfers for the same player
    player_market_values = valid_df.groupby(['player_name', 'age']).agg({
        'market_value_millions': 'mean',  # Average if multiple transfers
        'position': 'first',
        'nationality': 'first'
    }).reset_index()
    
    print(f"Loaded {len(player_market_values)} unique player-market value records from Transfermarkt")
    
    return player_market_values

def merge_with_player_data(player_df, transfermarkt_df):
    """
    Merge player data with transfermarkt market values
    
    Uses nested if statements for efficient matching
    
    Args:
        player_df: DataFrame with player stats (from All_Players.csv, etc.)
        transfermarkt_df: DataFrame with market values from transfermarkt
    
    Returns:
        DataFrame with merged data, including real market values where matched
    """
    if transfermarkt_df.empty:
        return player_df.copy()
    
    # Create a copy to avoid modifying original
    merged_df = player_df.copy()
    
    # Initialize market_value column if it doesn't exist
    if 'market_value' not in merged_df.columns:
        merged_df['market_value'] = None
    
    # Pre-process transfermarkt data: normalize names and convert ages
    transfermarkt_df = transfermarkt_df.copy()
    transfermarkt_df['name_normalized'] = transfermarkt_df['player_name'].astype(str).str.lower().str.strip()
    transfermarkt_df['age_int'] = pd.to_numeric(transfermarkt_df['age'], errors='coerce').astype('Int64')
    
    # Group transfermarkt by age for faster lookup
    tm_by_age = {}
    for age in transfermarkt_df['age_int'].dropna().unique():
        tm_by_age[int(age)] = transfermarkt_df[transfermarkt_df['age_int'] == age]
    
    # Try to match players by name and age
    matched_count = 0
    total_players = len(merged_df)
    
    print(f"Matching {total_players} players with Transfermarkt data...")
    
    for idx, player_row in merged_df.iterrows():
        player_name = player_row.get('Player', '')
        player_age = player_row.get('Age', None)
        
        # Skip if missing data
        if pd.isna(player_name) or player_name == '':
            continue
        if pd.isna(player_age):
            continue
        
        # Normalize player name and age
        player_name_norm = str(player_name).lower().strip()
        player_age_int = int(float(player_age))
        
        # Check if age exists in transfermarkt data
        if player_age_int in tm_by_age:
            age_matched_df = tm_by_age[player_age_int]
            
            # Try exact match first (nested if)
            exact_matches = age_matched_df[age_matched_df['name_normalized'] == player_name_norm]
            if len(exact_matches) > 0:
                merged_df.at[idx, 'market_value'] = exact_matches.iloc[0]['market_value_millions']
                matched_count += 1
            else:
                # Try fuzzy match only if exact match failed (nested if)
                for tm_idx, tm_row in age_matched_df.iterrows():
                    if fuzzy_match_name(player_name, tm_row['player_name']):
                        merged_df.at[idx, 'market_value'] = tm_row['market_value_millions']
                        matched_count += 1
                        break
        
        # Progress indicator every 1000 players
        if (idx + 1) % 1000 == 0:
            print(f"  Processed {idx + 1}/{total_players} players, matched: {matched_count}")
    
    print(f"Matched {matched_count} players with Transfermarkt market values")
    
    return merged_df

