CREATE TABLE gameweek (
	id INT NOT NULL AUTO_INCREMENT,
	start_datetime DATETIME,
	end_datetime DATETIME,
	my_projected_points FLOAT,
	my_points_scored FLOAT,
	PRIMARY KEY (id)
);