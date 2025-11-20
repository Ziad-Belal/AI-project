from src.data_loader import load_and_combine
from src.search import search_player
from src.status_check import is_active
from src.predictor import predict_player_value, predict_performance

# Load combined CSVs
players_df = load_and_combine()

# User input
name = input("Enter player name: ")

# Search for player
player = search_player(players_df, name)

if player is None:
    print("Player not found.")
    exit()

# Display basic info
print(f"\nPlayer: {player['Player']}")
print(f"Club: {player.get('Squad', 'Unknown')}")
print(f"Nation: {player.get('Nation', 'Unknown')}")
print(f"Position: {player.get('Pos', 'Unknown')}")
print(f"Age: {player.get('Age', 'Unknown')}")
print(f"Goals: {player.get('Gls', 'Unknown')}")
print(f"Assists: {player.get('Ast', 'Unknown')}")
print(f"Minutes Played: {player.get('MP', 'Unknown')}")

# Status check
if is_active(player):
    print("Status: ACTIVE")
else:
    print("Status: RETIRED / INACTIVE")

# Predictions
pred_value = predict_player_value(player)
pred_perf = predict_performance(player)

print(f"\nPredicted Market Value: {pred_value}")
print(f"Predicted Performance Next Season: {pred_perf}")
