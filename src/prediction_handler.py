import threading
import time
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.predictor import predict_player_value, predict_performance, predict_from_input
from src.status_check import is_active
from src.ui_utils import format_player_stats, format_input_stats

class PredictionHandler:
    def __init__(self, ui_callback):
        self.ui_callback = ui_callback
    
    def predict_from_input_async(self, goals, assists, minutes, age):
        """Run prediction in background thread"""
        threading.Thread(
            target=self._run_input_prediction,
            args=(goals, assists, minutes, age),
            daemon=True
        ).start()
    
    def _run_input_prediction(self, goals, assists, minutes, age):
        """Run input prediction"""
        steps = [
            "⚽ Processing Input Data...",
            "🤖 Running ML Models...",
            "📊 Calculating Predictions...",
            "✨ Generating Results..."
        ]
        
        for step in steps:
            self.ui_callback(step, is_final=False, result_data=None)
            time.sleep(0.8)
        
        result = predict_from_input(goals, assists, minutes, age)
        stats_text = format_input_stats(goals, assists, minutes, age, result)
        
        self.ui_callback(None, is_final=True, result_data={
            'stats_text': stats_text,
            'is_input': True
        })
    
    def search_and_predict_async(self, query, players_df):
        """Run search and prediction in background thread"""
        threading.Thread(
            target=self._run_search_prediction,
            args=(query, players_df),
            daemon=True
        ).start()
    
    def _run_search_prediction(self, query, players_df):
        """Run search prediction"""
        from src.search import smart_search
        
        player = smart_search(query, players_df)
        if player is None:
            self.ui_callback(f"❌ No matching player found for: '{query}'", 
                           is_final=True, result_data={'error': True})
            return
        
        steps = [
            "⚽ Loading Player Data...",
            "🤖 Selecting ML Features...",
            "📊 Processing with Models...",
            "✨ Generating Predictions..."
        ]
        
        for step in steps:
            self.ui_callback(step, is_final=False, result_data=None)
            time.sleep(0.8)
        
        pred_value = predict_player_value(player)
        pred_perf = predict_performance(player)
        status = "✅ ACTIVE" if is_active(player) else "❌ RETIRED / INACTIVE"
        
        stats_text = format_player_stats(player, pred_value, pred_perf, status)
        
        self.ui_callback(None, is_final=True, result_data={
            'stats_text': stats_text,
            'is_input': False
        })
