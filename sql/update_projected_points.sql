UPDATE player_gameweek 
SET xMins = %s, projected_points = %s, gameweek_id = %s
WHERE player_id = %s AND squad_gameweek_id = %s;