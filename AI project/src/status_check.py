def is_active(player_row):
    """
    Check if a player is active based on minutes played (MP).
    If MP > 0, player is considered active.
    If MP is missing or cannot be converted to int, player is inactive.
    """
    try:
        # Safely get MP value (works with both dict and pandas Series)
        if hasattr(player_row, 'get'):
            mp_val = player_row.get('MP', 0)
        else:
            mp_val = player_row['MP'] if 'MP' in player_row else 0
        
        if mp_val is None or mp_val == '':
            return False
        
        return int(float(mp_val)) > 0
    except (ValueError, TypeError, KeyError):
        # If MP is not a number, then player is considered retired/inactive
        return False 