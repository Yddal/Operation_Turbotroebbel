CREATE DATABASE IF NOT EXISTS fagskolen;
USE fagskolen;


CREATE TABLE IF NOT EXISTS courses
( 
	course_id VARCHAR(16) PRIMARY KEY,
    course_title VARCHAR(100),
    credits NUMERIC(3, 2),
    url VARCHAR(200),
    study_level VARCHAR(100),
    lear_out_know VARCHAR(400),
    lear_out_skills VARCHAR(400),
    lear_out_competence VARCHAR(400)
);

CREATE TABLE IF NOT EXISTS study_place
(
	location_id SMALLINT,
    location_name VARCHAR(150),
	CONSTRAINT study_place PRIMARY KEY (location_id)
);

CREATE TABLE IF NOT EXISTS study_programs
(
	study_id VARCHAR(200) PRIMARY KEY,
    study_title VARCHAR(100),
    study_description VARCHAR(400),
    location_id SMALLINT,
    credits DECIMAL (3, 2),
    study_language VARCHAR(50),
    study_lvl VARCHAR(60),
    why_choose VARCHAR(2000),
    what_learn VARCHAR(2000),
    teaching_format VARCHAR(500),
    mandatory_attendance VARCHAR(1000),
    police_certificate BOOLEAN,
    career_opportunities VARCHAR(2000),
    contact_info VARCHAR(400),
    study_url VARCHAR(400),
    course_id VARCHAR(16),
	CONSTRAINT courseID_FK
		FOREIGN KEY(course_id)
        REFERENCES courses(course_id),
    CONSTRAINT study_place_FK
		FOREIGN KEY(location_id)
        REFERENCES study_place(location_id)
);