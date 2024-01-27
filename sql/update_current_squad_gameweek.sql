UPDATE squad_gameweek
SET xG = %s, xGC = %s
WHERE squad_id = %s AND gameweek_id = %s;