UPDATE gameweek
SET is_current = 0, mean_player_points_delta = (
	SELECT AVG(projected_points - points_scored)
	FROM player_gameweek
	WHERE gameweek_id = 22
)
WHERE id = 22;