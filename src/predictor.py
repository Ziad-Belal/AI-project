"""
ML-based Predictor for Football Player Performance and Market Value
Uses trained Random Forest models to make predictions
"""
import numpy as np
import os
import sys

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from model_trainer import load_models, safe_convert
except ImportError:
    # Fallback if relative import doesn't work
    import model_trainer
    load_models = model_trainer.load_models
    safe_convert = model_trainer.safe_convert

# Load models once at module import (lazy loading)
PERF_MODEL = None
VALUE_MODEL = None
SCALER = None
MODELS_LOADED = False

def _ensure_models_loaded():
    """Lazy load models when needed"""
    global PERF_MODEL, VALUE_MODEL, SCALER, MODELS_LOADED
    if not MODELS_LOADED:
        try:
            PERF_MODEL, VALUE_MODEL, SCALER = load_models()
            MODELS_LOADED = True
        except Exception as e:
            print(f"Warning: Could not load models: {e}")
            print("Using fallback prediction methods")
            MODELS_LOADED = False
            PERF_MODEL = VALUE_MODEL = SCALER = None

def predict_from_input(goals, assists, minutes_played, age):
    """
    Predict performance and market value from direct input values.
    
    Args:
        goals: Number of goals scored
        assists: Number of assists
        minutes_played: Total minutes played
        age: Player age
    
    Returns:
        dict with 'performance' and 'market_value' predictions
    """
    # Validate inputs
    goals = max(0, float(goals))
    assists = max(0, float(assists))
    minutes_played = max(0, float(minutes_played))
    age = max(16, min(50, float(age)))
    
    # Ensure models are loaded
    _ensure_models_loaded()
    
    # Prepare feature vector
    features = np.array([[goals, assists, minutes_played, age]])
    
    if MODELS_LOADED and SCALER is not None:
        # Use ML models
        features_scaled = SCALER.transform(features)
        
        # Predict performance (next match contribution score)
        perf_score = PERF_MODEL.predict(features_scaled)[0]
        
        # Convert performance score to goals and assists estimate
        # Performance score represents combined contribution
        # Distribute based on input ratio
        total_contribution = goals + assists * 0.8
        if total_contribution > 0:
            goals_ratio = goals / total_contribution
            assists_ratio = (assists * 0.8) / total_contribution
        else:
            goals_ratio = 0.5
            assists_ratio = 0.5
        
        # Scale to per-match estimate (assuming ~30-40 matches per season)
        matches_estimate = max(1, minutes_played / 90)
        per_match_perf = perf_score / max(1, matches_estimate / 35)
        
        predicted_goals = max(0, round(per_match_perf * goals_ratio, 1))
        predicted_assists = max(0, round(per_match_perf * assists_ratio * 1.25, 1))
        
        # Predict market value
        market_value = VALUE_MODEL.predict(features_scaled)[0]
        market_value = max(0.1, market_value)
    else:
        # Fallback prediction
        base_performance = goals + assists * 0.8
        if 23 <= age <= 28:
            age_multiplier = 1.1
        elif age < 23:
            age_multiplier = 0.95 + (age - 18) * 0.03
        else:
            age_multiplier = 1.0 - (age - 28) * 0.02
        
        time_factor = 1.0 if minutes_played > 2000 else (0.9 if minutes_played > 1000 else 0.7)
        per_match_perf = base_performance * age_multiplier * time_factor * 0.15
        
        total_contribution = goals + assists * 0.8
        if total_contribution > 0:
            goals_ratio = goals / total_contribution
            assists_ratio = (assists * 0.8) / total_contribution
        else:
            goals_ratio = 0.5
            assists_ratio = 0.5
        
        predicted_goals = max(0, round(per_match_perf * goals_ratio, 1))
        predicted_assists = max(0, round(per_match_perf * assists_ratio * 1.25, 1))
        
        # Fallback value calculation
        base_value = (goals * 2.5) + (assists * 1.8)
        if age < 23:
            age_value_factor = 1.3
        elif age <= 28:
            age_value_factor = 1.0
        else:
            age_value_factor = 0.6 - (age - 28) * 0.05
        
        consistency_factor = min(1.0, minutes_played / 2500)
        market_value = (base_value * age_value_factor * consistency_factor) / 10
        market_value = max(0.1, market_value)
        
        # Set perf_score for return
        perf_score = per_match_perf
    
    return {
        "predicted_goals": predicted_goals,
        "predicted_assists": predicted_assists,
        "performance_score": round(perf_score, 2),
        "market_value": market_value
    }

def predict_player_value(player_row):
    """
    Predict market value from player data row.
    Uses ML model if available, otherwise fallback.
    """
    def safe_get(key, default=0):
        try:
            if hasattr(player_row, 'get'):
                val = player_row.get(key, default)
            else:
                val = player_row[key] if key in player_row else default
            if val is None or val == '':
                return default
            return float(val)
        except (ValueError, TypeError, KeyError):
            return default

    goals = safe_get("Gls", 0)
    assists = safe_get("Ast", 0)
    minutes = safe_get("MP", 0) * 90  # Convert matches to minutes estimate
    min_played = safe_get("Min", minutes)
    age = safe_get("Age", 25)
    
    result = predict_from_input(goals, assists, min_played, age)
    return f"${round(result['market_value'], 2)}M"

def predict_performance(player_row):
    """
    Predict next match performance from player data row.
    Uses ML model if available, otherwise fallback.
    """
    def safe_get(key, default=0):
        try:
            if hasattr(player_row, 'get'):
                val = player_row.get(key, default)
            else:
                val = player_row[key] if key in player_row else default
            if val is None or val == '':
                return default
            return float(val)
        except (ValueError, TypeError, KeyError):
            return default

    goals = safe_get("Gls", 0)
    assists = safe_get("Ast", 0)
    minutes = safe_get("MP", 0) * 90
    min_played = safe_get("Min", minutes)
    age = safe_get("Age", 25)
    
    result = predict_from_input(goals, assists, min_played, age)
    return {
        "predicted_goals": result["predicted_goals"],
        "predicted_assists": result["predicted_assists"]
    }
