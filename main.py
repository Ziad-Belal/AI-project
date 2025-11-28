# gui_main_realistic_full.py
import customtkinter as ctk
import threading
import time

# Project modules (future-proofed imports)
from src.data_loader import load_and_combine
from src.search import search_player
from src.status_check import is_active
from src.predictor import predict_player_value, predict_performance

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AnimatedLabel(ctk.CTkLabel):
    def flash(self, duration=0.5):
        self.configure(fg_color="#1abc9c")
        self.after(int(duration * 1000), lambda: self.configure(fg_color="transparent"))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Football AI Prediction - Realistic GUI")
        self.geometry("1200x750")

        # Load CSV for optional future use
        self.players_df = load_and_combine()  # optional

        # Title
        self.label_title = ctk.CTkLabel(self, text="Football AI Player Prediction", font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=20)

        # Player Name
        self.entry_player = ctk.CTkEntry(self, placeholder_text="Enter Player Name", width=400, font=("Roboto", 14))
        self.entry_player.pack(pady=5)

        # Stats Entries
        self.entry_goals = ctk.CTkEntry(self, placeholder_text="Goals (Gls)", width=200)
        self.entry_goals.pack(pady=2)
        self.entry_assists = ctk.CTkEntry(self, placeholder_text="Assists (Ast)", width=200)
        self.entry_assists.pack(pady=2)
        self.entry_age = ctk.CTkEntry(self, placeholder_text="Age", width=200)
        self.entry_age.pack(pady=2)
        self.entry_minutes = ctk.CTkEntry(self, placeholder_text="Minutes Played (MP)", width=200)
        self.entry_minutes.pack(pady=2)

        # Predict Button
        self.button_predict = ctk.CTkButton(self, text="Predict", width=120, command=self.start_thread)
        self.button_predict.pack(pady=10)

        # Animation Frame
        self.frame_animation = ctk.CTkFrame(self, width=1100, height=500, corner_radius=15)
        self.frame_animation.pack(pady=20)
        self.frame_animation.pack_propagate(False)

    def start_thread(self):
        threading.Thread(target=self.run_animation).start()

    def run_animation(self):
        player_name = self.entry_player.get().strip()
        if not player_name:
            return

        # Clear frame
        for widget in self.frame_animation.winfo_children():
            widget.destroy()

        # Animation steps
        steps = [
            "Loading Player Data...",
            "Selecting Important Features...",
            "Cleaning and Normalizing Data...",
            "Model Processing / Prediction..."
        ]

        label_step = AnimatedLabel(self.frame_animation, text="", font=("Roboto", 18, "bold"))
        label_step.pack(pady=20)
        self.frame_animation.update()

        for step in steps:
            label_step.configure(text=step)
            label_step.flash()
            self.frame_animation.update()
            time.sleep(1)

        # Collect inputs (default 0 if empty)
        try:
            goals = float(self.entry_goals.get()) if self.entry_goals.get().strip() else 0
            assists = float(self.entry_assists.get()) if self.entry_assists.get().strip() else 0
            age = float(self.entry_age.get()) if self.entry_age.get().strip() else 25
            minutes = float(self.entry_minutes.get()) if self.entry_minutes.get().strip() else 0
        except:
            goals = assists = age = minutes = 0

        player_data = {
            "Player": player_name,
            "Gls": goals,
            "Ast": assists,
            "Age": age,
            "MP": minutes
        }

        # Generate predictions
        pred_value = predict_player_value(player_data)
        pred_perf = predict_performance(player_data)
        status = "ACTIVE"

        # Final dashboard
        for widget in self.frame_animation.winfo_children():
            widget.destroy()

        label_complete = ctk.CTkLabel(self.frame_animation, text="Prediction Complete!", font=("Roboto", 22, "bold"))
        label_complete.pack(pady=10)

        stats_text = (
            f"Name: {player_name}\n"
            f"Goals: {goals}\n"
            f"Assists: {assists}\n"
            f"Minutes Played: {minutes}\n"
            f"Age: {age}\n"
            f"Status: {status}\n\n"
            f"Predicted Market Value: {pred_value}\n"
            f"Predicted Goals Next Season: {pred_perf['predicted_goals']}\n"
            f"Predicted Assists Next Season: {pred_perf['predicted_assists']}"
        )

        final_label = AnimatedLabel(self.frame_animation, text="", font=("Roboto", 14), justify="left")
        final_label.pack(pady=20)

        # Animate text typing
        for i in range(len(stats_text)):
            final_label.configure(text=stats_text[:i + 1])
            self.frame_animation.update()
            time.sleep(0.01)


if __name__ == "__main__":
    app = App()
    app.mainloop()


