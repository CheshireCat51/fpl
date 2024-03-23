UPDATE player
SET matches_played = %s, minutes_played = %s, goals = %s, assists = %s, penalty_goals = %s, penalty_attempts = %s, yellow_cards = %s, red_cards = %s, xG = %s, xA = %s, npxG = %s, progressive_carries = %s, progressive_passes = %s, goals_per_90 = %s, assists_per_90 = %s, xG_per_90 = %s, xA_per_90 = %s, npxG_per_90 = %s
WHERE id = %s;