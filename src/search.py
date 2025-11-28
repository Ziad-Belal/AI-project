def search_player(df, name):
    player = df[df['Player'].str.lower() == name.lower()]
    if player.empty:
        return None
    return player.iloc[0]
