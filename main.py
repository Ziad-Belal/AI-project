import customtkinter as ctk
import threading
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
        
        self.players_df = None
        threading.Thread(target=self._load_data, daemon=True).start()
        
        self._setup_ui()
        self.prediction_handler = PredictionHandler(self._on_prediction_update)

    def _setup_ui(self):
        self.main_container = ctk.CTkFrame(self, fg_color=FIELD_DARK_GREEN, corner_radius=0)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._setup_header()
        
        self.tabview = ctk.CTkTabview(
            self.main_container,
            fg_color=FIELD_GREEN,
            corner_radius=15,
            border_width=2,
            border_color=WHITE,
            height=200
        )
        self.tabview.pack(fill="x", pady=(0, 20))
        
        self.tab_input = self.tabview.add("📊 Direct Input")
        self.input_tab = InputTab(self.tab_input, self._on_input_predict)
        
        self.tab_search = self.tabview.add("🔍 Search Player")
        self.search_tab = SearchTab(self.tab_search, self._on_search)
        
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
        
        self.results_display = ResultsDisplay(self.frame_animation)

    def _setup_header(self):
        self.header_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=FIELD_GREEN,
            corner_radius=20,
            border_width=3,
            border_color=GOLD
        )
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        self.label_title = ctk.CTkLabel(
            self.header_frame,
            text="⚽ Football AI Prediction System ⚽",
            font=("Roboto", 40, "bold"),
            text_color=GOLD,
            fg_color="transparent"
        )
        self.label_title.pack(pady=(20, 5))
        
        self.label_subtitle = ctk.CTkLabel(
            self.header_frame,
            text="Machine Learning Powered Player Performance & Market Value Predictor",
            font=("Roboto", 18),
            text_color=WHITE,
            fg_color="transparent"
        )
        self.label_subtitle.pack(pady=(0, 20))

    def _load_data(self):
        try:
            self.players_df = load_and_combine()
        except Exception as e:
            print(f"Error loading data: {e}")

    def _on_input_predict(self, *args, is_error=False):
        if is_error:
            error_msg = args[0] if args else "Unknown error"
            self.results_display.show_message(error_msg, is_error=True)
            return
        
        if len(args) == 4:
            goals, assists, minutes, age = args
            self.prediction_handler.predict_from_input_async(goals, assists, minutes, age)
        else:
            self.results_display.show_message("⚠️ Invalid input!", is_error=True)

    def _on_search(self, query, is_error=False):
        if is_error:
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
        if is_final:
            if result_data and result_data.get('error'):
                self.after_idle(
                    lambda msg=step_text: self.results_display.show_message(msg, is_error=True)
                )
            elif result_data and 'stats_text' in result_data:
                self.after_idle(
                    lambda stats=result_data['stats_text']: self.results_display.show_results(stats)
                )
        else:
            if step_text:
                self.after_idle(
                    lambda text=step_text: self.results_display.show_step(text)
                )

if __name__ == "__main__":
    app = App()
    app.mainloop()
