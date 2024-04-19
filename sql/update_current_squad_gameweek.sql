UPDATE squad_gameweek
SET gameweek_id = %s, xG = %s, xGC = %s
WHERE squad_id = %s AND opposition_id = %s AND venue = '%s';