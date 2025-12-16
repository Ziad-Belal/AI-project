import customtkinter as ctk

# Colors
FIELD_DARK_GREEN = "#1a4d2e"
FIELD_GREEN = "#2d6a4f"
FIELD_LIGHT_GREEN = "#40916c"
WHITE = "#ffffff"
GOLD = "#ffd700"
DARK_GRAY = "#1e1e1e"
RED = "#dc2626"

class AnimatedLabel(ctk.CTkLabel):
    def flash(self, duration=0.5):
        self.configure(fg_color=FIELD_LIGHT_GREEN)
        self.after(int(duration*1000), lambda: self.configure(fg_color="transparent"))

class InputTab:
    def __init__(self, parent_tab, predict_callback):
        self.tab = parent_tab
        self.predict_callback = predict_callback
        self._setup_ui()
    
    def _setup_ui(self):
        instructions = ctk.CTkLabel(
            self.tab,
            text="Enter player statistics to predict next match performance and market value:",
            font=("Roboto", 16, "bold"),
            text_color=WHITE,
            fg_color="transparent"
        )
        instructions.pack(pady=(15, 20))
        
        input_container = ctk.CTkFrame(self.tab, fg_color="transparent")
        input_container.pack(pady=10)
        
        self.entry_goals = self._create_input_field(input_container, "Goals:", "0", 120)
        self.entry_assists = self._create_input_field(input_container, "Assists:", "0", 120)
        self.entry_minutes = self._create_input_field(input_container, "Minutes Played:", "0", 150)
        self.entry_age = self._create_input_field(input_container, "Age:", "25", 120)
        
        self.button_predict = ctk.CTkButton(
            self.tab,
            text="🎯 Predict Performance & Value",
            width=300,
            height=50,
            command=self._on_predict,
            font=("Roboto", 20, "bold"),
            fg_color=GOLD,
            hover_color="#ffed4e",
            text_color=DARK_GRAY,
            corner_radius=10,
            border_width=2,
            border_color=WHITE
        )
        self.button_predict.pack(pady=20)
    
    def _create_input_field(self, parent, label_text, placeholder, width):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", padx=15)
        
        ctk.CTkLabel(frame, text=label_text, font=("Roboto", 14, "bold"), text_color=WHITE).pack()
        
        entry = ctk.CTkEntry(
            frame,
            placeholder_text=placeholder,
            width=width,
            height=40,
            font=("Roboto", 16),
            corner_radius=10,
            fg_color=WHITE,
            text_color=DARK_GRAY
        )
        entry.pack(pady=(5, 0))
        return entry
    
    def _on_predict(self):
        try:
            goals = float(self.entry_goals.get() or 0)
            assists = float(self.entry_assists.get() or 0)
            minutes = float(self.entry_minutes.get() or 0)
            age = float(self.entry_age.get() or 25)
            
            if goals < 0 or assists < 0 or minutes < 0 or age < 16 or age > 50:
                self.predict_callback(
                    "⚠️ Invalid input values!\nPlease enter valid numbers:\n- Goals/Assists: ≥ 0\n- Minutes: ≥ 0\n- Age: 16-50",
                    is_error=True
                )
                return
            
            self.predict_callback(goals, assists, minutes, age)
        except ValueError:
            self.predict_callback("⚠️ Please enter valid numbers for all fields!", is_error=True)

class SearchTab:
    def __init__(self, parent_tab, search_callback):
        self.tab = parent_tab
        self.search_callback = search_callback
        self._setup_ui()
    
    def _setup_ui(self):
        self.search_label = ctk.CTkLabel(
            self.tab,
            text="Search for a Player in Database",
            font=("Roboto", 18, "bold"),
            text_color=WHITE,
            fg_color="transparent"
        )
        self.search_label.pack(pady=(20, 15))
        
        self.search_input_frame = ctk.CTkFrame(self.tab, fg_color="transparent")
        self.search_input_frame.pack(pady=(0, 20))
        
        self.entry_player = ctk.CTkEntry(
            self.search_input_frame,
            placeholder_text="Type player name (e.g., 'Messi', 'Ronaldo')",
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
            command=self._on_search,
            font=("Roboto", 18, "bold"),
            fg_color=GOLD,
            hover_color="#ffed4e",
            text_color=DARK_GRAY,
            corner_radius=10,
            border_width=2,
            border_color=WHITE
        )
        self.button_search.pack(side="left")
    
    def _on_search(self):
        query = self.entry_player.get()
        if not query:
            try:
                self.search_callback("⚠️ Please enter a player name!", is_error=True)
            except TypeError:
                self.search_callback(query)
            return
        self.search_callback(query)

class ResultsDisplay:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.current_widget = None
    
    def clear(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.current_widget = None
    
    def show_message(self, message, is_error=False):
        self.clear()
        label = ctk.CTkLabel(
            self.frame,
            text=message,
            font=("Roboto", 20, "bold"),
            text_color=RED if is_error else WHITE,
            fg_color="transparent"
        )
        label.pack(pady=50)
        self.current_widget = label
    
    def show_step(self, step_text):
        self.clear()
        label = AnimatedLabel(
            self.frame,
            text=step_text,
            font=("Roboto", 26, "bold"),
            text_color=GOLD,
            fg_color="transparent"
        )
        label.pack(pady=50)
        label.flash()
        self.current_widget = label
    
    def show_results(self, stats_text):
        import sys
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        from src.ui_utils import format_stats_text
        
        self.clear()
        
        label_complete = ctk.CTkLabel(
            self.frame,
            text="✅ Prediction Complete!",
            font=("Roboto", 36, "bold"),
            text_color=GOLD,
            fg_color="transparent"
        )
        label_complete.pack(pady=(20, 10))
        
        results_card = ctk.CTkFrame(
            self.frame,
            fg_color=FIELD_DARK_GREEN,
            corner_radius=15,
            border_width=2,
            border_color=GOLD
        )
        results_card.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        
        formatted_stats = format_stats_text(stats_text)
        
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
        text_widget.insert("1.0", formatted_stats)
        text_widget.configure(state="disabled")
        
        self.current_widget = results_card
