UPDATE squad_gameweek
SET gameweek_id = %s, overall_strength = %s, attack_strength = %s, defence_strength = %s
WHERE squad_id = %s AND opposition_id = %s AND venue = '%s';