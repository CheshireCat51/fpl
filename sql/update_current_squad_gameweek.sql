UPDATE squad_gameweek
SET sgw.gameweek_id = %s, xG = %s, xGC = %s
WHERE squad_id = %s AND sgw.opposition_id = %s AND sgw.venue = %s