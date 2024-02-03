WITH WeightedMinutes AS (
   SELECT
     pgw.player_id,
     SUM(CASE WHEN (23-6) <= pgw.gameweek_id THEN minutes_played * 0.7 ELSE minutes_played * 0.3 END) AS weighted_minutes,
     SUM(CASE WHEN (23-6) <= pgw.gameweek_id THEN 0.7 ELSE 0.3 END) AS weight_sum,
     AVG(pgw.minutes_played) AS non_weighted_avg
   FROM
      player_gameweek pgw
   WHERE
   	pgw.started = 1 AND
   	pgw.gameweek_id < 23
   GROUP BY
      pgw.player_id
)
SELECT
    player_id,
    p.name,
    weighted_minutes/weight_sum,
    non_weighted_avg
FROM
    WeightedMinutes
JOIN
	player p ON WeightedMinutes.player_id = p.id
