UPDATE gameweek
SET is_current = 1, my_points_scored = %s, mean_points_scored = %s
WHERE id = %s;