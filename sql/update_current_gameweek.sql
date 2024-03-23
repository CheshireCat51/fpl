UPDATE gameweek
SET is_current = 1, my_points_scored = %s, mean_points_scored = %s, mean_player_points_delta = (
	SELECT AVG(projected_points - points_scored)
	FROM player_gameweek
	WHERE projected_points IS NOT NULL AND gameweek_id = %s
)
WHERE id = %s;