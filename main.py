# main.py
# Football AI Prediction System - Main GUI
import customtkinter as ctk  # type: ignore
import threading
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import load_and_combine
from src.search import smart_search
from src.status_check import is_active
from src.predictor import predict_player_value, predict_performance, predict_from_input

# Football theme colors
FIELD_DARK_GREEN = "#1a4d2e"      # Dark green field background
FIELD_GREEN = "#2d6a4f"           # Medium green for cards
FIELD_LIGHT_GREEN = "#40916c"     # Light green accents
WHITE = "#ffffff"                 # White for text and lines
GOLD = "#ffd700"                  # Gold for highlights
DARK_GRAY = "#1e1e1e"             # Dark gray for contrast
RED = "#dc2626"                   # Red for errors/important

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AnimatedLabel(ctk.CTkLabel):
    def flash(self, duration=0.5):
        self.configure(fg_color=FIELD_LIGHT_GREEN)
        self.after(int(duration*1000), lambda: self.configure(fg_color="transparent"))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚽ Football AI Prediction System ⚽")
        self.geometry("1600x1000")
        self.configure(fg_color=FIELD_DARK_GREEN)

        # Load data in background
        self.players_df = None
        threading.Thread(target=self._load_data, daemon=True).start()

        # Main container with scrollable frame
        self.main_container = ctk.CTkFrame(self, fg_color=FIELD_DARK_GREEN, corner_radius=0)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header section
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
        self._setup_direct_input_tab()
        
        # Tab 2: Search Player
        self.tab_search = self.tabview.add("🔍 Search Player")
        self._setup_search_tab()

        # Results frame - larger and scrollable
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

    def _load_data(self):
        """Load player data in background"""
        try:
            self.players_df = load_and_combine()
        except Exception as e:
            print(f"Error loading data: {e}")

    def _setup_direct_input_tab(self):
        """Setup the direct input tab"""
        # Instructions
        instructions = ctk.CTkLabel(
            self.tab_input,
            text="Enter player statistics to predict next match performance and market value:",
            font=("Roboto", 16, "bold"),
            text_color=WHITE,
            fg_color="transparent"
        )
        instructions.pack(pady=(15, 20))

        # Input fields container
        input_container = ctk.CTkFrame(self.tab_input, fg_color="transparent")
        input_container.pack(pady=10)

        # Goals input
        goals_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        goals_frame.pack(side="left", padx=15)
        ctk.CTkLabel(
            goals_frame,
            text="Goals:",
            font=("Roboto", 14, "bold"),
            text_color=WHITE
        ).pack()
        self.entry_goals = ctk.CTkEntry(
            goals_frame,
            placeholder_text="0",
            width=120,
            height=40,
            font=("Roboto", 16),
            corner_radius=10,
            fg_color=WHITE,
            text_color=DARK_GRAY
        )
        self.entry_goals.pack(pady=(5, 0))

        # Assists input
        assists_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        assists_frame.pack(side="left", padx=15)
        ctk.CTkLabel(
            assists_frame,
            text="Assists:",
            font=("Roboto", 14, "bold"),
            text_color=WHITE
        ).pack()
        self.entry_assists = ctk.CTkEntry(
            assists_frame,
            placeholder_text="0",
            width=120,
            height=40,
            font=("Roboto", 16),
            corner_radius=10,
            fg_color=WHITE,
            text_color=DARK_GRAY
        )
        self.entry_assists.pack(pady=(5, 0))

        # Minutes Played input
        minutes_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        minutes_frame.pack(side="left", padx=15)
        ctk.CTkLabel(
            minutes_frame,
            text="Minutes Played:",
            font=("Roboto", 14, "bold"),
            text_color=WHITE
        ).pack()
        self.entry_minutes = ctk.CTkEntry(
            minutes_frame,
            placeholder_text="0",
            width=150,
            height=40,
            font=("Roboto", 16),
            corner_radius=10,
            fg_color=WHITE,
            text_color=DARK_GRAY
        )
        self.entry_minutes.pack(pady=(5, 0))

        # Age input
        age_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        age_frame.pack(side="left", padx=15)
        ctk.CTkLabel(
            age_frame,
            text="Age:",
            font=("Roboto", 14, "bold"),
            text_color=WHITE
        ).pack()
        self.entry_age = ctk.CTkEntry(
            age_frame,
            placeholder_text="25",
            width=120,
            height=40,
            font=("Roboto", 16),
            corner_radius=10,
            fg_color=WHITE,
            text_color=DARK_GRAY
        )
        self.entry_age.pack(pady=(5, 0))

        # Predict button
        self.button_predict = ctk.CTkButton(
            self.tab_input,
            text="🎯 Predict Performance & Value",
            width=300,
            height=50,
            command=self.predict_from_input,
            font=("Roboto", 20, "bold"),
            fg_color=GOLD,
            hover_color="#ffed4e",
            text_color=DARK_GRAY,
            corner_radius=10,
            border_width=2,
            border_color=WHITE
        )
        self.button_predict.pack(pady=20)

    def _setup_search_tab(self):
        """Setup the search player tab"""
        # Search label
        self.search_label = ctk.CTkLabel(
            self.tab_search,
            text="Search for a Player in Database",
            font=("Roboto", 18, "bold"),
            text_color=WHITE,
            fg_color="transparent"
        )
        self.search_label.pack(pady=(20, 15))

        # Search input container
        self.search_input_frame = ctk.CTkFrame(self.tab_search, fg_color="transparent")
        self.search_input_frame.pack(pady=(0, 20))

        # single unified entry field (accepts natural-language queries)
        self.entry_player = ctk.CTkEntry(
            self.search_input_frame, 
            placeholder_text="Type any word or phrase (e.g., 'Messi', 'top scorer', 'Barcelona defender')", 
            width=650, 
            height=50,
            font=("Roboto", 16),
            corner_radius=10,
            fg_color=WHITE,
            text_color=DARK_GRAY,
            placeholder_text_color="#666666",
            border_width=2,
            border_color=FIELD_LIGHT_GREEN
        )
        self.entry_player.pack(side="left", padx=(0, 15))

        self.button_search = ctk.CTkButton(
            self.search_input_frame, 
            text="🔍 Search", 
            width=150, 
            height=50,
            command=self.start_search_thread,
            font=("Roboto", 18, "bold"),
            fg_color=GOLD,
            hover_color="#ffed4e",
            text_color=DARK_GRAY,
            corner_radius=10,
            border_width=2,
            border_color=WHITE
        )
        self.button_search.pack(side="left")

    def predict_from_input(self):
        """Predict from direct input values"""
        try:
            goals = float(self.entry_goals.get() or 0)
            assists = float(self.entry_assists.get() or 0)
            minutes = float(self.entry_minutes.get() or 0)
            age = float(self.entry_age.get() or 25)
            
            if goals < 0 or assists < 0 or minutes < 0 or age < 16 or age > 50:
                self._show_message("⚠️ Invalid input values!\nPlease enter valid numbers:\n- Goals/Assists: ≥ 0\n- Minutes: ≥ 0\n- Age: 16-50", is_error=True)
                return
            
            # Start prediction in thread
            threading.Thread(target=self._run_input_prediction, args=(goals, assists, minutes, age), daemon=True).start()
        except ValueError:
            self._show_message("⚠️ Please enter valid numbers for all fields!", is_error=True)

    def _run_input_prediction(self, goals, assists, minutes, age):
        """Run prediction from input in background thread"""
        # Clear frame
        self.after_idle(self._clear_frame)
        
        # Animation steps
        steps = [
            "⚽ Processing Input Data...",
            "🤖 Running ML Models...",
            "📊 Calculating Predictions...",
            "✨ Generating Results..."
        ]
        
        for i, step in enumerate(steps):
            step_text = step
            delay_ms = i * 800
            if i == 0:
                self.after_idle(lambda s=step_text: self._show_step(s))
            else:
                self.after(delay_ms, lambda s=step_text: self._update_step(s))
        
        time.sleep(len(steps) * 0.8)
        
        # Generate predictions
        result = predict_from_input(goals, assists, minutes, age)
        
        # Format results
        stats_text = (
            f"📋 INPUT STATISTICS\n"
            f"{'='*50}\n"
            f"Goals Scored: {goals}\n"
            f"Assists: {assists}\n"
            f"Minutes Played: {int(minutes)}\n"
            f"Age: {int(age)}\n\n"
            f"🎯 NEXT MATCH PREDICTION\n"
            f"{'='*50}\n"
            f"Predicted Goals: {result['predicted_goals']}\n"
            f"Predicted Assists: {result['predicted_assists']}\n"
            f"Performance Score: {result['performance_score']}\n\n"
            f"💰 MARKET VALUE ESTIMATE\n"
            f"{'='*50}\n"
            f"Estimated Transfer Value: ${round(result['market_value'], 2)}M\n"
        )
        
        self.after(len(steps) * 800 + 500, lambda: self._show_results(stats_text, is_input=True))

    def start_search_thread(self):
        """Start search in background thread"""
        threading.Thread(target=self.run_search_animation, daemon=True).start()

    def run_search_animation(self):
        """Run search and prediction animation"""
        raw_query = self.entry_player.get()
        if not raw_query:
            self.after_idle(lambda: self._show_message("⚠️ Please enter a player name or query!", is_error=True))
            return
        
        if self.players_df is None:
            self.after_idle(lambda: self._show_message("⏳ Loading player database...\nPlease wait and try again.", is_error=False))
            return

        # Clear frame
        self.after_idle(self._clear_frame)

        # Search player using smart_search
        player = smart_search(raw_query, self.players_df)
        if player is None:
            self.after_idle(lambda q=raw_query: self._show_message(f"❌ No matching player or result found for: '{q}'", is_error=True))
            return

        # Animation steps
        steps = [
            "⚽ Loading Player Data...",
            "🤖 Selecting ML Features...",
            "📊 Processing with Models...",
            "✨ Generating Predictions..."
        ]

        for i, step in enumerate(steps):
            step_text = step
            delay_ms = i * 800
            if i == 0:
                self.after_idle(lambda s=step_text: self._show_step(s))
            else:
                self.after(delay_ms, lambda s=step_text: self._update_step(s))

        time.sleep(len(steps) * 0.8)

        # Generate predictions
        pred_value = predict_player_value(player)
        pred_perf = predict_performance(player)
        status = "✅ ACTIVE" if is_active(player) else "❌ RETIRED / INACTIVE"

        def safe_get(data, key, default='Unknown'):
            if hasattr(data, 'get'):
                try:
                    val = data.get(key, default)
                    return val if val is not None and val != '' else default
                except:
                    try:
                        return data[key] if key in data else default
                    except:
                        return default
            return default

        # Format results
        stats_text = (
            f"👤 PLAYER INFORMATION\n"
            f"{'='*50}\n"
            f"Name: {safe_get(player, 'Player')}\n"
            f"Club: {safe_get(player, 'Squad')}\n"
            f"Nation: {safe_get(player, 'Nation')}\n"
            f"Position: {safe_get(player, 'Pos')}\n"
            f"Age: {safe_get(player, 'Age')}\n"
            f"Goals: {safe_get(player, 'Gls')}\n"
            f"Assists: {safe_get(player, 'Ast')}\n"
            f"Minutes Played: {safe_get(player, 'MP')}\n"
            f"Status: {status}\n\n"
            f"🎯 NEXT MATCH PREDICTION\n"
            f"{'='*50}\n"
            f"Predicted Goals: {pred_perf['predicted_goals']}\n"
            f"Predicted Assists: {pred_perf['predicted_assists']}\n\n"
            f"💰 MARKET VALUE ESTIMATE\n"
            f"{'='*50}\n"
            f"Estimated Transfer Value: {pred_value}\n"
        )

        self.after(len(steps) * 800 + 500, lambda: self._show_results(stats_text, is_input=False))

    def _clear_frame(self):
        """Thread-safe frame clearing"""
        for widget in self.frame_animation.winfo_children():
            widget.destroy()

    def _show_message(self, message, is_error=False):
        """Thread-safe message display"""
        for widget in self.frame_animation.winfo_children():
            widget.destroy()
        error_label = ctk.CTkLabel(
            self.frame_animation, 
            text=message, 
            font=("Roboto", 20, "bold"),
            text_color=RED if is_error else WHITE,
            fg_color="transparent"
        )
        error_label.pack(pady=50)

    def _show_step(self, step_text):
        """Thread-safe step display"""
        for widget in self.frame_animation.winfo_children():
            widget.destroy()
        label = AnimatedLabel(
            self.frame_animation, 
            text=step_text, 
            font=("Roboto", 26, "bold"),
            text_color=GOLD,
            fg_color="transparent"
        )
        label.pack(pady=50)
        label.flash()

    def _update_step(self, step_text):
        """Thread-safe step update"""
        for widget in self.frame_animation.winfo_children():
            if isinstance(widget, AnimatedLabel):
                widget.configure(text=step_text, text_color=GOLD)
                widget.flash()
                break

    def _show_results(self, stats_text, is_input=False):
        """Thread-safe results display with scrollable text"""
        for widget in self.frame_animation.winfo_children():
            widget.destroy()

        # Success header
        label_complete = ctk.CTkLabel(
            self.frame_animation, 
            text="✅ Prediction Complete!", 
            font=("Roboto", 36, "bold"),
            text_color=GOLD,
            fg_color="transparent"
        )
        label_complete.pack(pady=(20, 10))

        # Results card container
        results_card = ctk.CTkFrame(
            self.frame_animation,
            fg_color=FIELD_DARK_GREEN,
            corner_radius=15,
            border_width=2,
            border_color=GOLD
        )
        results_card.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        # Format stats with better structure
        formatted_stats = self._format_stats_text(stats_text)
        
        # Use Textbox widget for scrollable content with larger text
        text_widget = ctk.CTkTextbox(
            results_card,
            font=("Roboto", 22, "normal"),
            text_color=WHITE,
            fg_color=FIELD_DARK_GREEN,
            corner_radius=10,
            border_width=2,
            border_color=GOLD,
            wrap="word"
        )
        text_widget.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Insert formatted text
        text_widget.insert("1.0", formatted_stats)
        text_widget.configure(state="disabled")  # Make it read-only

    def _format_stats_text(self, stats_text):
        """Format stats text with better structure and spacing"""
        lines = stats_text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if '=' in line and len(line.strip()) > 10:
                # Section separator - make it more prominent
                formatted_lines.append('')
                formatted_lines.append(line)
                formatted_lines.append('')
            elif ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    # Add more spacing and make it clearer
                    formatted_lines.append(f"  {key:.<35} {value}")
                else:
                    formatted_lines.append(line)
            elif line.strip() == '':
                formatted_lines.append('')
            else:
                # Headers and other text
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)

if __name__ == "__main__":
    app = App()
    app.mainloop()
