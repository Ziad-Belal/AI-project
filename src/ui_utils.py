def safe_get(data, key, default='Unknown'):
    """Get value from player data safely"""
    try:
        if hasattr(data, 'get'):
            val = data.get(key, default)
        else:
            val = data[key] if key in data else default
        return val if val is not None and val != '' else default
    except:
        return default

def format_player_stats(player, pred_value, pred_perf, status):
    """Format player stats for display"""
    return (
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

def format_input_stats(goals, assists, minutes, age, result):
    """Format input stats for display"""
    return (
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

def format_stats_text(stats_text):
    """Format stats text nicely"""
    lines = stats_text.split('\n')
    formatted = []
    
    for line in lines:
        if '=' in line and len(line.strip()) > 10:
            formatted.append('')
            formatted.append(line)
            formatted.append('')
        elif ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                formatted.append(f"  {key:.<35} {value}")
            else:
                formatted.append(line)
        else:
            formatted.append(line)
    
    return '\n'.join(formatted)
