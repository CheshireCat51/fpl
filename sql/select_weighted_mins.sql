SELECT
(t0.late_sum*7 + t1.early_sum*3)/(t0.late_count*7 + t1.early_count*3) AS 'WeightedAvg',
AVG(pgw.minutes_played) AS 'UnweightedAvg'
FROM player_gameweek pgw
	SELECT SUM(pgw.minutes_played) AS late_sum, COUNT(pgw.gameweek_id) AS late_count
	FROM player_gameweek pgw
	WHERE pgw.gameweek_id >= 17 AND pgw.gameweek_id < 22

	SELECT SUM(pgw.minutes_played) AS early_sum, COUNT(pgw.gameweek_id) AS early_count
	FROM player_gameweek pgw
	WHERE pgw.gameweek_id < 17
	
WHERE pgw.started = 1 AND pgw.player_id = 372