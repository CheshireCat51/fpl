CREATE TABLE my_team (
	id INT NOT NULL AUTO_INCREMENT,
	player_id INT NOT NULL,
	player_name VARCHAR(255) NOT NULL,
	`position` ENUM('GKP', 'DEF', 'MID', 'FWD'),
	is_captain BOOL,
	is_vice_captain BOOL,
	purchase_price FLOAT,
	current_price FLOAT,
	selling_price FLOAT,
	projected_points_for_next_gameweek FLOAT,
	PRIMARY KEY (id),
	FOREIGN KEY (player_id) REFERENCES player(id)
);