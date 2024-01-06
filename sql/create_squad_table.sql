CREATE TABLE player (
	id INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(255) NOT NULL,
	abbreviation VARCHAR(255) NOT NULL,
	overall_strength FLOAT,
	attack_strength FLOAT,
	defence_strength FLOAT,
	goals INT,
	assists INT,
	penalty_goals INT,
	penalty_attempts INT,
	yellow_cards INT,
	red_cards INT,
	xG FLOAT,
	npxG FLOAT,
	`xA` FLOAT,
	progressive_carries INT,
	progressive_passes INT,
	goals_per_90 INT,
	assists_per_90 INT,
	xG_per_90 FLOAT,
	npxG_per_90 FLOAT,
	xA_per_90 FLOAT,
	PRIMARY KEY (id)
);