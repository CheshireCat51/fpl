CREATE TABLE player (
	id INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(255) NOT NULL,
	squad_id INT NOT NULL,
	`position` ENUM('GKP', 'DEF', 'MID', 'FWD'),
	chance_of_playing_next_gameweek FLOAT,
	projected_points FLOAT,
	PRIMARY KEY (id),
	FOREIGN KEY (squad_id) REFERENCES squad(id)
);