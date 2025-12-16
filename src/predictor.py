import numpy as np
import os
import sys

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.model_trainer import load_models

# Global variables for models
PERF_MODEL = None
VALUE_MODEL = None
SCALER = None
MODELS_LOADED = False

def load_models_once():
    """Load models if not already loaded"""
    global PERF_MODEL, VALUE_MODEL, SCALER, MODELS_LOADED
    if not MODELS_LOADED:
        try:
            PERF_MODEL, VALUE_MODEL, SCALER = load_models()
            MODELS_LOADED = True
        except:
            MODELS_LOADED = False

def predict_from_input(goals, assists, minutes_played, age):
    """Predict performance and market value from input"""
    goals = max(0, float(goals))
    assists = max(0, float(assists))
    minutes_played = max(0, float(minutes_played))
    age = max(16, min(50, float(age)))
    
    load_models_once()
    features = np.array([[goals, assists, minutes_played, age]])
    
    if MODELS_LOADED and SCALER is not None:
        # Use ML models
        features_scaled = SCALER.transform(features)
        perf_score = PERF_MODEL.predict(features_scaled)[0]
        market_value = VALUE_MODEL.predict(features_scaled)[0]
        market_value = max(0.1, market_value)
        
        # Convert to goals/assists
        total = goals + assists * 0.8
        if total > 0:
            goals_ratio = goals / total
            assists_ratio = (assists * 0.8) / total
        else:
            goals_ratio = 0.5
            assists_ratio = 0.5
        
        matches = max(1, minutes_played / 90)
        per_match = perf_score / max(1, matches / 35)
        
        predicted_goals = max(0, round(per_match * goals_ratio, 1))
        predicted_assists = max(0, round(per_match * assists_ratio * 1.25, 1))
    else:
        # Simple fallback
        base = goals + assists * 0.8
        if 23 <= age <= 28:
            age_mult = 1.1
        elif age < 23:
            age_mult = 0.95 + (age - 18) * 0.03
        else:
            age_mult = 1.0 - (age - 28) * 0.02
        
        time_factor = 1.0 if minutes_played > 2000 else (0.9 if minutes_played > 1000 else 0.7)
        per_match = base * age_mult * time_factor * 0.15
        
        total = goals + assists * 0.8
        if total > 0:
            goals_ratio = goals / total
            assists_ratio = (assists * 0.8) / total
        else:
            goals_ratio = 0.5
            assists_ratio = 0.5
        
        predicted_goals = max(0, round(per_match * goals_ratio, 1))
        predicted_assists = max(0, round(per_match * assists_ratio * 1.25, 1))
        
        # Simple value calculation
        base_value = (goals * 2.5) + (assists * 1.8)
        if age < 23:
            age_factor = 1.3
        elif age <= 28:
            age_factor = 1.0
        else:
            age_factor = 0.6 - (age - 28) * 0.05
        
        consistency = min(1.0, minutes_played / 2500)
        market_value = (base_value * age_factor * consistency) / 10
        market_value = max(0.1, market_value)
        perf_score = per_match
    
    return {
        "predicted_goals": predicted_goals,
        "predicted_assists": predicted_assists,
        "performance_score": round(perf_score, 2),
        "market_value": market_value
    }

def get_numeric(player_row, key, default=0):
    """Get numeric value from player data"""
    try:
        if hasattr(player_row, 'get'):
            val = player_row.get(key, default)
        else:
            val = player_row[key] if key in player_row else default
        if val is None or val == '':
            return default
        return float(val)
    except:
        return default

def predict_player_value(player_row):
    """Predict market value for a player"""
    goals = get_numeric(player_row, "Gls", 0)
    assists = get_numeric(player_row, "Ast", 0)
    minutes = get_numeric(player_row, "MP", 0) * 90
    min_played = get_numeric(player_row, "Min", minutes)
    age = get_numeric(player_row, "Age", 25)
    
    result = predict_from_input(goals, assists, min_played, age)
    return f"${round(result['market_value'], 2)}M"

def predict_performance(player_row):
    """Predict next match performance for a player"""
    goals = get_numeric(player_row, "Gls", 0)
    assists = get_numeric(player_row, "Ast", 0)
    minutes = get_numeric(player_row, "MP", 0) * 90
    min_played = get_numeric(player_row, "Min", minutes)
    age = get_numeric(player_row, "Age", 25)
    
    result = predict_from_input(goals, assists, min_played, age)
    return {
        "predicted_goals": result["predicted_goals"],
        "predicted_assists": result["predicted_assists"]
    }
