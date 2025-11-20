def is_active(player_row):
   
    try:
        return int(player_row.get('MP', 0)) > 0
    except ValueError:
        # If MP is not a number, then he will be considered retired/inactive
        return False

"here, what I said is that if the 'MP' (minutes played) value is greater than 0, the player is considered active. If the value cannot be converted to an integer (for example, if it's missing or not a number), the function will return False, indicating that the player is inactive."