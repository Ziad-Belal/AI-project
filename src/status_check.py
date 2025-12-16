def is_active(player_row):
    """Check if player is active"""
    try:
        if hasattr(player_row, 'get'):
            mp_val = player_row.get('MP', 0)
        else:
            mp_val = player_row['MP'] if 'MP' in player_row else 0
        
        if mp_val is None or mp_val == '':
            return False
        
        return int(float(mp_val)) > 0
    except:
        return False
