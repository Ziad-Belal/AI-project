# main.py
# Football AI Prediction System - Main GUI
import customtkinter as ctk  # type: ignore
import threading
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import load_and_combine
from src.prediction_handler import PredictionHandler
from src.ui_components import InputTab, SearchTab, ResultsDisplay, FIELD_DARK_GREEN, FIELD_GREEN, GOLD, WHITE

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚽ Football AI Prediction System ⚽")
        self.geometry("1600x1000")
        self.configure(fg_color=FIELD_DARK_GREEN)

        # Load data in background
        self.players_df = None
        threading.Thread(target=self._load_data, daemon=True).start()

        # Setup UI
        self._setup_ui()
        
        # Initialize prediction handler
        self.prediction_handler = PredictionHandler(self._on_prediction_update)

    def _setup_ui(self):
        """Setup the main UI components"""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color=FIELD_DARK_GREEN, corner_radius=0)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header section
        self._setup_header()

        # Create tabview for different input methods
        self.tabview = ctk.CTkTabview(
            self.main_container,
            fg_color=FIELD_GREEN,
            corner_radius=15,
            border_width=2,
            border_color=WHITE,
            height=200
        )
        self.tabview.pack(fill="x", pady=(0, 20))
        
        # Tab 1: Direct Input
        self.tab_input = self.tabview.add("📊 Direct Input")
        self.input_tab = InputTab(self.tab_input, self._on_input_predict)
        
        # Tab 2: Search Player
        self.tab_search = self.tabview.add("🔍 Search Player")
        self.search_tab = SearchTab(self.tab_search, self._on_search)

        # Results frame
        self.frame_animation = ctk.CTkFrame(
            self.main_container,
            width=1200,
            height=650,
            corner_radius=20,
            fg_color=FIELD_GREEN,
            border_width=3,
            border_color=GOLD
        )
        self.frame_animation.pack(fill="both", expand=True, pady=(0, 0))
        self.frame_animation.pack_propagate(False)
        
        # Results display component
        self.results_display = ResultsDisplay(self.frame_animation)

    def _setup_header(self):
        """Setup the header section"""
        self.header_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=FIELD_GREEN,
            corner_radius=20,
            border_width=3,
            border_color=GOLD
        )
        self.header_frame.pack(fill="x", pady=(0, 20))

        # Title
        self.label_title = ctk.CTkLabel(
            self.header_frame,
            text="⚽ Football AI Prediction System ⚽",
            font=("Roboto", 40, "bold"),
            text_color=GOLD,
            fg_color="transparent"
        )
        self.label_title.pack(pady=(20, 5))

        # Subtitle
        self.label_subtitle = ctk.CTkLabel(
            self.header_frame,
            text="Machine Learning Powered Player Performance & Market Value Predictor",
            font=("Roboto", 18),
            text_color=WHITE,
            fg_color="transparent"
        )
        self.label_subtitle.pack(pady=(0, 20))

    def _load_data(self):
        """Load player data in background"""
        try:
            self.players_df = load_and_combine()
        except Exception as e:
            print(f"Error loading data: {e}")

    def _on_input_predict(self, *args, is_error=False):
        """Handle input-based prediction request"""
        if is_error:
            # Handle error message (first arg is the error message string)
            error_msg = args[0] if args else "Unknown error"
            self.results_display.show_message(error_msg, is_error=True)
            return
        
        # Normal prediction call (4 numeric arguments: goals, assists, minutes, age)
        if len(args) == 4:
            goals, assists, minutes, age = args
            self.prediction_handler.predict_from_input_async(goals, assists, minutes, age)
        else:
            self.results_display.show_message("⚠️ Invalid input!", is_error=True)

    def _on_search(self, query, is_error=False):
        """Handle search request"""
        if is_error:
            # Handle error message
            self.results_display.show_message(query, is_error=True)
            return
            
        if self.players_df is None:
            self.results_display.show_message(
                "⏳ Loading player database...\nPlease wait and try again.",
                is_error=False
            )
            return
        self.prediction_handler.search_and_predict_async(query, self.players_df)

    def _on_prediction_update(self, step_text, is_final, result_data):
        """
        Callback for prediction handler updates.
        Called from background thread, so uses after() for thread safety.
        """
        if is_final:
            if result_data and result_data.get('error'):
                # Error message
                self.after_idle(
                    lambda msg=step_text: self.results_display.show_message(msg, is_error=True)
                )
            elif result_data and 'stats_text' in result_data:
                # Show results
                self.after_idle(
                    lambda stats=result_data['stats_text']: self.results_display.show_results(stats)
                )
        else:
            # Show animation step
            if step_text:
                self.after_idle(
                    lambda text=step_text: self.results_display.show_step(text)
                )


if __name__ == "__main__":
    app = App()
    app.mainloop()
