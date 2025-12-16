"""
Reusable UI components for the Football AI application
"""
import customtkinter as ctk

# Theme colors
FIELD_DARK_GREEN = "#1a4d2e"
FIELD_GREEN = "#2d6a4f"
FIELD_LIGHT_GREEN = "#40916c"
WHITE = "#ffffff"
GOLD = "#ffd700"
DARK_GRAY = "#1e1e1e"
RED = "#dc2626"

class AnimatedLabel(ctk.CTkLabel):
    """Label with flash animation capability"""
    def flash(self, duration=0.5):
        self.configure(fg_color=FIELD_LIGHT_GREEN)
        self.after(int(duration*1000), lambda: self.configure(fg_color="transparent"))

class InputTab:
    """Direct input tab component"""
    
    def __init__(self, parent_tab, predict_callback):
        self.tab = parent_tab
        self.predict_callback = predict_callback
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the direct input tab UI"""
        # Instructions
        instructions = ctk.CTkLabel(
            self.tab,
            text="Enter player statistics to predict next match performance and market value:",
            font=("Roboto", 16, "bold"),
            text_color=WHITE,
            fg_color="transparent"
        )
        instructions.pack(pady=(15, 20))
        
        # Input fields container
        input_container = ctk.CTkFrame(self.tab, fg_color="transparent")
        input_container.pack(pady=10)
        
        # Create input fields
        self.entry_goals = self._create_input_field(input_container, "Goals:", "0", 120)
        self.entry_assists = self._create_input_field(input_container, "Assists:", "0", 120)
        self.entry_minutes = self._create_input_field(input_container, "Minutes Played:", "0", 150)
        self.entry_age = self._create_input_field(input_container, "Age:", "25", 120)
        
        # Predict button
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
        """Create a labeled input field"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", padx=15)
        
        ctk.CTkLabel(
            frame,
            text=label_text,
            font=("Roboto", 14, "bold"),
            text_color=WHITE
        ).pack()
        
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
        """Handle predict button click"""
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
    
    def get_values(self):
        """Get current input values"""
        try:
            return {
                'goals': float(self.entry_goals.get() or 0),
                'assists': float(self.entry_assists.get() or 0),
                'minutes': float(self.entry_minutes.get() or 0),
                'age': float(self.entry_age.get() or 25)
            }
        except ValueError:
            return None

class SearchTab:
    """Search player tab component"""
    
    def __init__(self, parent_tab, search_callback):
        self.tab = parent_tab
        self.search_callback = search_callback
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the search tab UI"""
        # Search label
        self.search_label = ctk.CTkLabel(
            self.tab,
            text="Search for a Player in Database",
            font=("Roboto", 18, "bold"),
            text_color=WHITE,
            fg_color="transparent"
        )
        self.search_label.pack(pady=(20, 15))
        
        # Search input container
        self.search_input_frame = ctk.CTkFrame(self.tab, fg_color="transparent")
        self.search_input_frame.pack(pady=(0, 20))
        
        # Search entry field
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
        
        # Search button
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
        """Handle search button click"""
        query = self.entry_player.get()
        if not query:
            # Handle error case - callback might accept error messages
            if callable(self.search_callback):
                try:
                    self.search_callback("⚠️ Please enter a player name or query!", is_error=True)
                except TypeError:
                    # Fallback if callback doesn't accept is_error
                    self.search_callback(query)
            return
        self.search_callback(query)

class ResultsDisplay:
    """Results display component"""
    
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.current_widget = None
    
    def clear(self):
        """Clear the display"""
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.current_widget = None
    
    def show_message(self, message, is_error=False):
        """Show a message"""
        self.clear()
        error_label = ctk.CTkLabel(
            self.frame,
            text=message,
            font=("Roboto", 20, "bold"),
            text_color=RED if is_error else WHITE,
            fg_color="transparent"
        )
        error_label.pack(pady=50)
        self.current_widget = error_label
    
    def show_step(self, step_text):
        """Show an animation step"""
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
    
    def update_step(self, step_text):
        """Update the current step"""
        if isinstance(self.current_widget, AnimatedLabel):
            self.current_widget.configure(text=step_text, text_color=GOLD)
            self.current_widget.flash()
    
    def show_results(self, stats_text):
        """Show prediction results"""
        from ui_utils import format_stats_text
        
        self.clear()
        
        # Success header
        label_complete = ctk.CTkLabel(
            self.frame,
            text="✅ Prediction Complete!",
            font=("Roboto", 36, "bold"),
            text_color=GOLD,
            fg_color="transparent"
        )
        label_complete.pack(pady=(20, 10))
        
        # Results card container
        results_card = ctk.CTkFrame(
            self.frame,
            fg_color=FIELD_DARK_GREEN,
            corner_radius=15,
            border_width=2,
            border_color=GOLD
        )
        results_card.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        
        # Format and display stats
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

