import pandas as pd
import numpy as np
import os
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

def safe_convert(value, default=0):
    """Convert value to float safely"""
    try:
        if pd.isna(value) or value == '' or value is None:
            return default
        return float(value)
    except:
        return default

def prepare_data():
    """Load and prepare data from CSV files"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ve_dir = os.path.dirname(script_dir)
    
    csv1_path = os.path.join(ve_dir, "data", "All_Players.csv")
    csv2_path = os.path.join(ve_dir, "data", "Season.csv")
    
    df1 = pd.read_csv(csv1_path)
    df2 = pd.read_csv(csv2_path)
    df = pd.concat([df1, df2], ignore_index=True)
    
    features = []
    performance_targets = []
    value_targets = []
    
    for idx, row in df.iterrows():
        goals = safe_convert(row.get('Gls', 0))
        assists = safe_convert(row.get('Ast', 0))
        minutes = safe_convert(row.get('MP', 0))
        age = safe_convert(row.get('Age', 25))
        
        if goals < 0 or assists < 0 or minutes < 0 or age < 16 or age > 50:
            continue
        
        min_played = safe_convert(row.get('Min', minutes * 90))
        features.append([goals, assists, min_played, age])
        
        # Performance target
        base_perf = goals + assists * 0.8
        if 23 <= age <= 28:
            age_mult = 1.1
        elif age < 23:
            age_mult = 0.95 + (age - 18) * 0.03
        else:
            age_mult = 1.0 - (age - 28) * 0.02
        
        time_factor = 1.0 if min_played > 2000 else (0.9 if min_played > 1000 else 0.7)
        predicted_perf = base_perf * age_mult * time_factor * 0.15
        performance_targets.append(max(0, predicted_perf))
        
        # Value target
        base_value = (goals * 2.5) + (assists * 1.8)
        if age < 23:
            age_factor = 1.3
        elif age <= 28:
            age_factor = 1.0
        else:
            age_factor = 0.6 - (age - 28) * 0.05
        
        consistency = min(1.0, min_played / 2500)
        estimated_value = (base_value * age_factor * consistency) / 10
        value_targets.append(max(0.1, estimated_value))
    
    return np.array(features), np.array(performance_targets), np.array(value_targets)

def train_models():
    """Train ML models"""
    print("Loading data...")
    X, y_perf, y_value = prepare_data()
    
    if len(X) == 0:
        raise ValueError("No valid data found")
    
    print(f"Training on {len(X)} samples...")
    
    # Split 80% train, 20% test
    X_train, X_test, y_perf_train, y_perf_test, y_value_train, y_value_test = train_test_split(
        X, y_perf, y_value, test_size=0.2, random_state=42
    )
    
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train performance model
    print("Training performance model...")
    perf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    perf_model.fit(X_train_scaled, y_perf_train)
    
    perf_pred = perf_model.predict(X_test_scaled)
    perf_mae = mean_absolute_error(y_perf_test, perf_pred)
    perf_r2 = r2_score(y_perf_test, perf_pred)
    print(f"Performance Model - MAE: {perf_mae:.3f}, R²: {perf_r2:.3f}")
    
    # Train value model
    print("Training value model...")
    value_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    value_model.fit(X_train_scaled, y_value_train)
    
    value_pred = value_model.predict(X_test_scaled)
    value_mae = mean_absolute_error(y_value_test, value_pred)
    value_r2 = r2_score(y_value_test, value_pred)
    print(f"Value Model - MAE: ${value_mae:.2f}M, R²: {value_r2:.3f}")
    
    # Save models
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
