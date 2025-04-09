UPDATE player_gameweek pgw
JOIN player p ON pgw.player_id = p.id
SET pgw.squad_gameweek_id = %s
WHERE pgw.gameweek_id = %s AND p.squad_id = %s AND pgw.squad_gameweek_id IS NULL