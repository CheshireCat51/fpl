CREATE TABLE player_gameweek (
	id INT NOT NULL AUTO_INCREMENT,
	player_id INT NOT NULL,
	gameweek_id INT NOT NULL,
	started BOOL,
	minutes_played INT,
	`goals` INT(10) NULL DEFAULT NULL,
	`assists` INT(10) NULL DEFAULT NULL,
	`penalty_goals` INT(10) NULL DEFAULT NULL,
	`penalty_attempts` INT(10) NULL DEFAULT NULL,
	`yellow_cards` INT(10) NULL DEFAULT NULL,
	`red_cards` INT(10) NULL DEFAULT NULL,
	`xG` FLOAT NULL DEFAULT NULL,
	`npxG` FLOAT NULL DEFAULT NULL,
	`xA` FLOAT NULL DEFAULT NULL,
	`progressive_carries` INT(10) NULL DEFAULT NULL,
	`progressive_passes` INT(10) NULL DEFAULT NULL,
	projected_points FLOAT,
	points_scored INT,
	PRIMARY KEY (id),
	FOREIGN KEY (player_id) REFERENCES player(id),
	FOREIGN KEY (gameweek_id) REFERENCES gameweek(id)
);