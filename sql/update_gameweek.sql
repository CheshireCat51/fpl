UPDATE gameweek
SET my_points_scored = %s, mean_points_scored = %s
WHERE id = %s;
UPDATE gameweek
SET is_current = 1, my_projected_points = %s
WHERE id = %s;