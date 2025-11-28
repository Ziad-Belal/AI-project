"""
Machine Learning Model Trainer for Football Player Predictions
Trains models to predict next match performance and market value
"""
import pandas as pd
import numpy as np
import os
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

def safe_convert(value, default=0):
    """Safely convert value to float"""
    try:
        if pd.isna(value) or value == '' or value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def prepare_data():
    """Load and prepare data from CSV files"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory (ve folder)
    ve_dir = os.path.dirname(script_dir)
    
    # CSV paths
    csv1_path = os.path.join(ve_dir, "data", "All_Players.csv")
    csv2_path = os.path.join(ve_dir, "data", "Season.csv")
    
    # Load CSVs
    df1 = pd.read_csv(csv1_path)
    df2 = pd.read_csv(csv2_path)
    
    # Combine both CSVs
    df = pd.concat([df1, df2], ignore_index=True)
    
    # Prepare features and targets
    features = []
    performance_targets = []  # For next match performance (goals + assists)
    value_targets = []  # For market value estimation
    
    for idx, row in df.iterrows():
        # Input features
        goals = safe_convert(row.get('Gls', 0))
        assists = safe_convert(row.get('Ast', 0))
        minutes = safe_convert(row.get('MP', 0))  # Matches played
        age = safe_convert(row.get('Age', 25))
        
        # Skip rows with invalid data
        if goals < 0 or assists < 0 or minutes < 0 or age < 16 or age > 50:
            continue
        
        # Calculate minutes played (if Min column exists, use it, otherwise estimate from MP)
        min_played = safe_convert(row.get('Min', minutes * 90))
        
        # Features: goals, assists, minutes played, age
        features.append([goals, assists, min_played, age])
        
        # For performance prediction: predict next match goals and assists
        # We'll use a simple approach: if we have historical data, use trends
        # Otherwise, use current stats as baseline
        # For training, we'll create synthetic targets based on patterns
        # In a real scenario, you'd use next season/match data
        
        # Performance target: next match performance score
        # Based on current form, age, and playing time
        base_performance = goals + assists * 0.8  # Assists weighted slightly less
        
        # Age factor (peak performance around 25-28)
        if 23 <= age <= 28:
            age_multiplier = 1.1
        elif age < 23:
            age_multiplier = 0.95 + (age - 18) * 0.03  # Growing potential
        else:
            age_multiplier = 1.0 - (age - 28) * 0.02  # Decline after 28
        
        # Playing time factor
        if min_played > 2000:  # Regular starter
            time_factor = 1.0
        elif min_played > 1000:
            time_factor = 0.9
        else:
            time_factor = 0.7
        
        # Predicted next match performance (goals + assists)
        predicted_performance = base_performance * age_multiplier * time_factor * 0.15  # Per match estimate
        performance_targets.append(max(0, predicted_performance))
        
        # Market value target: based on goals, assists, age, and playing time
        # Formula: base value from performance, adjusted by age and consistency
        base_value = (goals * 2.5) + (assists * 1.8)
        
        # Age premium/discount
        if age < 23:
            age_value_factor = 1.3  # Young players have higher potential value
        elif age <= 28:
            age_value_factor = 1.0  # Peak age
        else:
            age_value_factor = 0.6 - (age - 28) * 0.05  # Declining value
        
        # Playing time consistency factor
        consistency_factor = min(1.0, min_played / 2500)  # Full season is ~2500-3000 mins
        
        # Estimated market value in millions
        estimated_value = (base_value * age_value_factor * consistency_factor) / 10
        value_targets.append(max(0.1, estimated_value))
    
    return np.array(features), np.array(performance_targets), np.array(value_targets)

def train_models():
    """Train ML models for performance and value prediction"""
    print("Loading and preparing data...")
    X, y_perf, y_value = prepare_data()
    
    if len(X) == 0:
        raise ValueError("No valid data found in CSV files")
    
    print(f"Training on {len(X)} samples...")
    
    # Split data
    X_train, X_test, y_perf_train, y_perf_test, y_value_train, y_value_test = train_test_split(
        X, y_perf, y_value, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train performance prediction model
    print("Training performance prediction model...")
    perf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    perf_model.fit(X_train_scaled, y_perf_train)
    
    perf_pred = perf_model.predict(X_test_scaled)
    perf_mae = mean_absolute_error(y_perf_test, perf_pred)
    perf_r2 = r2_score(y_perf_test, perf_pred)
    print(f"Performance Model - MAE: {perf_mae:.3f}, R²: {perf_r2:.3f}")
    
    # Train value prediction model
    print("Training market value prediction model...")
    value_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    value_model.fit(X_train_scaled, y_value_train)
    
    value_pred = value_model.predict(X_test_scaled)
    value_mae = mean_absolute_error(y_value_test, value_pred)
    value_r2 = r2_score(y_value_test, value_pred)
    print(f"Value Model - MAE: ${value_mae:.2f}M, R²: {value_r2:.3f}")
    
    # Save models and scaler
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ve_dir = os.path.dirname(script_dir)
    models_dir = os.path.join(ve_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    with open(os.path.join(models_dir, "perf_model.pkl"), "wb") as f:
        pickle.dump(perf_model, f)
    
    with open(os.path.join(models_dir, "value_model.pkl"), "wb") as f:
        pickle.dump(value_model, f)
    
    with open(os.path.join(models_dir, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)
    
    print(f"Models saved to {models_dir}")
    return perf_model, value_model, scaler

def load_models():
    """Load trained models"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ve_dir = os.path.dirname(script_dir)
    models_dir = os.path.join(ve_dir, "models")
    
    try:
        with open(os.path.join(models_dir, "perf_model.pkl"), "rb") as f:
            perf_model = pickle.load(f)
        
        with open(os.path.join(models_dir, "value_model.pkl"), "rb") as f:
            value_model = pickle.load(f)
        
        with open(os.path.join(models_dir, "scaler.pkl"), "rb") as f:
            scaler = pickle.load(f)
        
        return perf_model, value_model, scaler
    except FileNotFoundError:
        print("Models not found. Training new models...")
        return train_models()

if __name__ == "__main__":
    train_models()

