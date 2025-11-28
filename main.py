# gui_main_realistic.py
import customtkinter as ctk
import threading
import time
from src.data_loader import load_and_combine
from src.search import search_player
from src.status_check import is_active
from src.predictor import predict_player_value, predict_performance

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AnimatedLabel(ctk.CTkLabel):
    def flash(self, duration=0.5):
        self.configure(fg_color="#1abc9c")
        self.after(int(duration*1000), lambda: self.configure(fg_color="transparent"))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Football AI Prediction - Realistic GUI")
        self.geometry("1200x700")

        self.players_df = load_and_combine()

        # Title
        self.label_title = ctk.CTkLabel(self, text="Football AI Player Prediction", font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=20)

        # Search
        self.entry_player = ctk.CTkEntry(self, placeholder_text="Enter Player Name", width=400, font=("Roboto", 14))
        self.entry_player.pack(pady=10)
        self.button_search = ctk.CTkButton(self, text="Search", width=120, command=self.start_thread)
        self.button_search.pack(pady=5)

        # Animation frame
        self.frame_animation = ctk.CTkFrame(self, width=1100, height=500, corner_radius=15)
        self.frame_animation.pack(pady=20)
        self.frame_animation.pack_propagate(False)

    def start_thread(self):
        threading.Thread(target=self.run_animation).start()

    def run_animation(self):
        player_name = self.entry_player.get()
        if not player_name:
            return

        for widget in self.frame_animation.winfo_children():
            widget.destroy()

        # Search player
        player = search_player(self.players_df, player_name)
        if player is None:
            ctk.CTkLabel(self.frame_animation, text="Player not found.", font=("Roboto", 16)).pack(pady=20)
            return

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

        # Generate predictions
        pred_value = predict_player_value(player)
        pred_perf = predict_performance(player)
        status = "ACTIVE" if is_active(player) else "RETIRED / INACTIVE"

        # Final dashboard
        for widget in self.frame_animation.winfo_children():
            widget.destroy()

        label_complete = ctk.CTkLabel(self.frame_animation, text="Prediction Complete!", font=("Roboto", 22, "bold"))
        label_complete.pack(pady=10)

        stats_text = (
            f"Name: {player.get('Player','Unknown')}\n"
            f"Club: {player.get('Squad','Unknown')}\n"
            f"Nation: {player.get('Nation','Unknown')}\n"
            f"Position: {player.get('Pos','Unknown')}\n"
            f"Age: {player.get('Age','Unknown')}\n"
            f"Goals: {player.get('Gls','Unknown')}\n"
            f"Assists: {player.get('Ast','Unknown')}\n"
            f"Minutes Played: {player.get('MP','Unknown')}\n"
            f"Status: {status}\n\n"
            f"Predicted Market Value: {pred_value}\n"
            f"Predicted Performance Next Season: {pred_perf}"
        )

        final_label = AnimatedLabel(self.frame_animation, text=stats_text, font=("Roboto", 14), justify="left")
        final_label.pack(pady=20)

        # Optional: animate label appearance like AI assistant
        for i in range(len(stats_text)):
            final_label.configure(text=stats_text[:i+1])
            self.frame_animation.update()
            time.sleep(0.01)

if __name__ == "__main__":
    app = App()
    app.mainloop()


