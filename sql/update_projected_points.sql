UPDATE player_gameweek 
SET projected_points = %s
WHERE player_id = %s AND gameweek_id = %s;