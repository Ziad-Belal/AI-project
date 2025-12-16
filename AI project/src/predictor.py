"""
ML-based Predictor for Football Player Performance and Market Value
Uses trained Random Forest or Neural Network models to make predictions
"""
import numpy as np
import os
import sys
import pickle

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from model_trainer import load_models, safe_convert
    from neural_network import NeuralNetwork
except ImportError:
    # Fallback if relative import doesn't work
    import model_trainer
    load_models = model_trainer.load_models
    safe_convert = model_trainer.safe_convert
    try:
        import neural_network
        NeuralNetwork = neural_network.NeuralNetwork
    except ImportError:
        NeuralNetwork = None

# Load models once at module import (lazy loading)
PERF_MODEL = None
VALUE_MODEL = None
SCALER = None
MODELS_LOADED = False
USE_NEURAL_NETWORK = False

def _ensure_models_loaded():
    """Lazy load models when needed - tries neural network first, then random forest"""
    global PERF_MODEL, VALUE_MODEL, SCALER, MODELS_LOADED, USE_NEURAL_NETWORK
    if not MODELS_LOADED:
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ve_dir = os.path.dirname(script_dir)
            models_dir = os.path.join(ve_dir, "models")
            
            # Try to load neural network models first
            try:
                if NeuralNetwork is not None:
                    perf_model_path = os.path.join(models_dir, "perf_model_nn.pkl")
                    value_model_path = os.path.join(models_dir, "value_model_nn.pkl")
                    scaler_path = os.path.join(models_dir, "scaler.pkl")
                    
                    if os.path.exists(perf_model_path) and os.path.exists(value_model_path):
                        PERF_MODEL = NeuralNetwork.load(perf_model_path)
                        VALUE_MODEL = NeuralNetwork.load(value_model_path)
                        with open(scaler_path, 'rb') as f:
                            import pickle
                            SCALER = pickle.load(f)
                        USE_NEURAL_NETWORK = True
                        MODELS_LOADED = True
                        print("Loaded Neural Network models")
                        return
            except Exception as e:
                print(f"Could not load neural network models: {e}")
            
            # Fallback to Random Forest models
            PERF_MODEL, VALUE_MODEL, SCALER = load_models()
            USE_NEURAL_NETWORK = False
            MODELS_LOADED = True
            print("Loaded Random Forest models")
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
        if USE_NEURAL_NETWORK:
            perf_score = PERF_MODEL.predict(features_scaled)[0][0]
        else:
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
        if USE_NEURAL_NETWORK:
            market_value = VALUE_MODEL.predict(features_scaled)[0][0]
        else:
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
        
        # Fallback value calculation (calibrated slightly higher)
        base_value = (goals * 2.5) + (assists * 1.8)
        if age < 23:
            age_value_factor = 1.3
        elif age <= 28:
            age_value_factor = 1.0
        else:
            # Prevent overly harsh penalties for older players
            age_value_factor = max(0.2, 0.6 - (age - 28) * 0.05)
        
        consistency_factor = min(1.0, minutes_played / 2500)
        # Previously divided by 10; divide by 5 to avoid under-valuing in fallback mode
        market_value = (base_value * age_value_factor * consistency_factor) / 5
        market_value = max(0.5, market_value)
        
        # Set perf_score for return
        perf_score = per_match_perf
    
    return {
        "predicted_goals": predicted_goals,
        "predicted_assists": predicted_assists,
        "performance_score": round(perf_score, 2),
        "market_value": market_value
    }

def _safe_get_numeric(player_row, key, default=0):
    """
    Safely extract numeric value from player data.
    Centralized to avoid duplication.
    """
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

def predict_player_value(player_row):
    """
    Predict market value from player data row.
    Uses ML model if available, otherwise fallback.
    """
    goals = _safe_get_numeric(player_row, "Gls", 0)
    assists = _safe_get_numeric(player_row, "Ast", 0)
    minutes = _safe_get_numeric(player_row, "MP", 0) * 90  # Convert matches to minutes estimate
    min_played = _safe_get_numeric(player_row, "Min", minutes)
    age = _safe_get_numeric(player_row, "Age", 25)
    
    result = predict_from_input(goals, assists, min_played, age)
    return f"${round(result['market_value'], 2)}M"

def predict_performance(player_row):
    """
    Predict next match performance from player data row.
    Uses ML model if available, otherwise fallback.
    """
    goals = _safe_get_numeric(player_row, "Gls", 0)
    assists = _safe_get_numeric(player_row, "Ast", 0)
    minutes = _safe_get_numeric(player_row, "MP", 0) * 90
    min_played = _safe_get_numeric(player_row, "Min", minutes)
    age = _safe_get_numeric(player_row, "Age", 25)
    
    result = predict_from_input(goals, assists, min_played, age)
    return {
        "predicted_goals": result["predicted_goals"],
        "predicted_assists": result["predicted_assists"]
    }
