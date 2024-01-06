CREATE TABLE squad_gameweek (
	id INT NOT NULL AUTO_INCREMENT,
	squad_id INT NOT NULL,
	gameweek_id INT NOT NULL,
	overall_strength FLOAT,
	overall_strength_change FLOAT,
	attack_strength FLOAT,
	attack_strength_change FLOAT,
	defence_strength FLOAT,
	defence_strength_change FLOAT,
	PRIMARY KEY (id),
	FOREIGN KEY (squad_id) REFERENCES squad(id),
	FOREIGN KEY (gameweek_id) REFERENCES gameweek(id)
);