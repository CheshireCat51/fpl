squad_column_map = {
    'Squad': 'name',
    'MP': 'matches_played',
    'Gls': 'goals',
    'Ast': 'assists',
    'PK': 'penalty_goals',
    'PKatt': 'penalty_attempts',
    'CrdY': 'yellow_cards',
    'CrdR': 'red_cards',
    'xG': 'xG',
    'xAG': 'xA',
    'npxG': 'npxG',
    'PrgC': 'progressive_carries',
    'PrgP': 'progressive_passes',
    'Gls.1': 'goals_per_90',
    'Ast.1': 'assists_per_90',
    'xG.1': 'xG_per_90',
    'xAG.1': 'xA_per_90',
    'npxG.1': 'npxG_per_90'
}

squad_gw_column_map = {
    'Date': 'date',
    'Round': 'gameweek_id',
    'Opponent': 'name',
    'Venue': 'venue',
    'xG': 'xG',
    'xGA': 'xGC',
    'GF': 'goals_scored',
    'GA': 'goals_conceded'
}

team_strength_column_map = {
    'Attack': 'attack_strength',
    'Defence': 'defence_strength',
    'Overall': 'overall_strength'
}

player_column_map = {
    'Player': 'name',
    'Pos': 'position',
    'MP': 'matches_played',
    'Min': 'minutes_played',
    'Gls': 'goals',
    'Ast': 'assists',
    'PK': 'penalty_goals',
    'PKatt': 'penalty_attempts',
    'CrdY': 'yellow_cards',
    'CrdR': 'red_cards',
    'xG': 'xG',
    'npxG': 'npxG',
    'xAG': 'xA',
    'PrgC': 'progressive_carries',
    'PrgP': 'progressive_passes',
    'Gls.1': 'goals_per_90',
    'Ast.1': 'assists_per_90',
    'xG.1': 'xG_per_90',
    'xAG.1': 'xA_per_90',
    'npxG.1': 'npxG_per_90'
}

player_gw_column_map = {
    'Date': 'date',
    'Round': 'gameweek_id',
    'Opponent': 'name',
    'Start': 'started',
    'Min': 'minutes_played',
    'Gls': 'goals',
    'Ast': 'assists',
    'PK': 'penalty_goals',
    'PKatt': 'penalty_attempts',
    'CrdY': 'yellow_cards',
    'CrdR': 'red_cards',
    'xG': 'xG',
    'xAG': 'xA',
    'npxG': 'npxG',
}

player_gw_defensive_column_map = {
    'Date': 'date',
    'Round': 'gameweek_id',
    'Opponent': 'name',
    'Blocks': 'blocks',
    'Tkl': 'tackles',
    'Int': 'interceptions',
    'Clr': 'clearances',
    'Min': 'minutes_played',
}

player_gw_misc_column_map = {
    'Date': 'date',
    'Round': 'gameweek_id',
    'Opponent': 'name',
    'Recov': 'recoveries',
    'Min': 'minutes_played',
}