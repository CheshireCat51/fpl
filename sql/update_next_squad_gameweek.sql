UPDATE squad_gameweek
SET overall_strength = %s, attack_strength = %s, defence_strength = %s
WHERE squad_id = %s AND gameweek_id = %s;