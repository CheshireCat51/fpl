DELETE pgw1
FROM player_gameweek pgw1
INNER JOIN player_gameweek pgw2
WHERE pgw1.id > pgw2.id AND pgw1.player_id = pgw2.player_id AND pgw1.gameweek_id = pgw2.gameweek_id