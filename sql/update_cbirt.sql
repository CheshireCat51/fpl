UPDATE player_gameweek
SET clearances = %s,
    blocks = %s,
    interceptions = %s,
    recoveries = %s,
    tackles = %s
WHERE player_id = %s AND squad_gameweek_id = %s;