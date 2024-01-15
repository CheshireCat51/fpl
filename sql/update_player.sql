UPDATE my_team
SET player_id = %s, is_captain = %s, is_vice_captain = %s, is_benched = %s, purchase_price = %s, selling_price = %s
WHERE id = %s;