def predict_player_value(player_row):
    """
    Very simple estimation model.
    Uses goals, assists, age, and league strength.
    """

    try:
        goals = float(player_row.get("Gls", 0))
    except:
        goals = 0

    try:
        assists = float(player_row.get("Ast", 0))
    except:
        assists = 0

    try:
        age = float(player_row.get("Age", 30))
    except:
        age = 30

    # Base performance score
    performance = (goals * 4) + (assists * 3)

    # Age factor (younger = higher value)
    if age < 23:
        age_factor = 1.5
    elif age <= 28:
        age_factor = 1.2
    else:
        age_factor = 0.8

    # Final estimated value
    value = performance * age_factor * 1.8

    return f"${round(value, 2)}M"



def predict_performance(player_row):
    """
    Predict next season performance based on Gls, Ast, MP.
    """

    try:
        goals = float(player_row.get("Gls", 0))
    except:
        goals = 0

    try:
        assists = float(player_row.get("Ast", 0))
    except:
        assists = 0

    try:
        minutes = float(player_row.get("MP", 0))
    except:
        minutes = 0

    # Basic prediction model
    predicted_goals = goals * 1.10      # +10%
    predicted_assists = assists * 1.08  # +8%

    if minutes < 500:
        predicted_goals *= 0.7
        predicted_assists *= 0.7

    return {
        "predicted_goals": round(predicted_goals, 2),
        "predicted_assists": round(predicted_assists, 2)
    }
