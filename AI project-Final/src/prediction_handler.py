"""
Business logic handler for predictions
Separates prediction logic from UI code
"""
import threading
import time
import sys
import os

# Add src directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from predictor import predict_player_value, predict_performance, predict_from_input
from status_check import is_active
from ui_utils import format_player_stats, format_input_stats

class PredictionHandler:
    """Handles prediction operations and callbacks"""
    
    def __init__(self, ui_callback):
        """
        Args:
            ui_callback: Function to call with (step_text, is_final, result_data)
        """
        self.ui_callback = ui_callback
    
    def predict_from_input_async(self, goals, assists, minutes, age):
        """Run input-based prediction asynchronously"""
        threading.Thread(
            target=self._run_input_prediction,
            args=(goals, assists, minutes, age),
            daemon=True
        ).start()
    
    def _run_input_prediction(self, goals, assists, minutes, age):
        """Run prediction from input in background thread"""
        steps = [
            "⚽ Processing Input Data...",
            "🤖 Running ML Models...",
            "📊 Calculating Predictions...",
            "✨ Generating Results..."
        ]
        
        for i, step in enumerate(steps):
            self.ui_callback(step, is_final=False, result_data=None)
            time.sleep(0.8)
        
        # Generate predictions
        result = predict_from_input(goals, assists, minutes, age)
        stats_text = format_input_stats(goals, assists, minutes, age, result)
        
        self.ui_callback(None, is_final=True, result_data={
            'stats_text': stats_text,
            'is_input': True
        })
    
    def search_and_predict_async(self, query, players_df):
        """Run search and prediction asynchronously"""
        threading.Thread(
            target=self._run_search_prediction,
            args=(query, players_df),
            daemon=True
        ).start()
    
    def _run_search_prediction(self, query, players_df):
        """Run search and prediction in background thread"""
        from search import search_player_only
        
        # Search player by name only (no extra heuristics)
        player = search_player_only(query, players_df)
        if player is None:
            self.ui_callback(f"❌ No matching player found for: '{query}'", 
                           is_final=True, result_data={'error': True})
            return
        
        # Animation steps
        steps = [
            "⚽ Loading Player Data...",
            "🤖 Selecting ML Features...",
            "📊 Processing with Models...",
            "✨ Generating Predictions..."
        ]
        
        for step in steps:
            self.ui_callback(step, is_final=False, result_data=None)
            time.sleep(0.8)
        
        # Generate predictions
        pred_value = predict_player_value(player)
        pred_perf = predict_performance(player)
        status = "✅ ACTIVE" if is_active(player) else "❌ RETIRED / INACTIVE"
        
        stats_text = format_player_stats(player, pred_value, pred_perf, status)
        
        self.ui_callback(None, is_final=True, result_data={
            'stats_text': stats_text,
            'is_input': False
        })

