UPDATE player_gameweek
SET `started` = %s, minutes_played = %s, goals = %s, assists = %s, penalty_goals = %s, penalty_attempts = %s, yellow_cards = %s, red_cards = %s, clearances = %s, blocks = %s, interceptions = %s, recoveries = %s, tackles = %s, xG = %s, npxG = %s, xA = %s, points_scored = %s
WHERE player_id = %s AND squad_gameweek_id = %s;