CREATE DATABASE IF NOT EXISTS fagskolen;
USE fagskolen;


CREATE TABLE IF NOT EXISTS courses
( 
	course_id VARCHAR(20) PRIMARY KEY,
    course_title VARCHAR(500),
    credits NUMERIC(12, 5),
    url VARCHAR(200),
    study_level VARCHAR(100),
    lear_out_know TEXT,
    lear_out_skills TEXT,
    lear_out_competence TEXT
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
    study_title VARCHAR(400),
    study_description VARCHAR(600),
    location_id SMALLINT,
    credits DECIMAL (12, 5),
    study_language VARCHAR(50),
    study_lvl VARCHAR(100),
    why_choose TEXT,
    what_learn TEXT,
    teaching_format TEXT,
    mandatory_attendance TEXT,
    police_certificate BOOLEAN,
    career_opportunities TEXT,
    contact_info TEXT,
    study_url TEXT,
    course_id VARCHAR(20),
	CONSTRAINT courseID_fk
		FOREIGN KEY(course_id)
        REFERENCES courses(course_id),
    CONSTRAINT study_place_fk
		FOREIGN KEY(location_id)
        REFERENCES study_place(location_id)
);

CREATE TABLE IF NOT EXISTS lookuptalbe_study_course
(
	study_id VARCHAR(200),
    course_id VARCHAR(20),
    CONSTRAINT study_course_pk PRIMARY KEY (study_id, course_id),
    CONSTRAINT study_id_fk
		FOREIGN KEY(study_id)
        REFERENCES study_programs(study_id),
	CONSTRAINT course_id_fk
		FOREIGN KEY(course_id)
        REFERENCES courses(course_id)
);
