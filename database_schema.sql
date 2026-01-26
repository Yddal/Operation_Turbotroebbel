-- ============================================================================
-- MySQL Database Schema for Study Programs and Courses
-- ============================================================================
-- This schema defines the database structure for storing study program
-- information extracted from the website.
-- ============================================================================

-- Study Programs Table
CREATE TABLE study_programs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  description LONGTEXT,
  credits INT,
  language VARCHAR(100),
  level VARCHAR(100),
  why_choose LONGTEXT,
  what_learn LONGTEXT,
  teaching_format VARCHAR(255),
  mandatory_attendance LONGTEXT,
  police_certificate VARCHAR(255),
  career_opportunities LONGTEXT,
  contact_info LONGTEXT,
  study_url VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_title (title),
  INDEX idx_level (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Courses/Subjects Table
CREATE TABLE courses (
  id INT PRIMARY KEY AUTO_INCREMENT,
  study_program_id INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  credits VARCHAR(50),
  study_level VARCHAR(100),
  url VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (study_program_id) REFERENCES study_programs(id) ON DELETE CASCADE,
  INDEX idx_study_program (study_program_id),
  INDEX idx_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Learning Outcomes Table
CREATE TABLE learning_outcomes (
  id INT PRIMARY KEY AUTO_INCREMENT,
  course_id INT NOT NULL,
  knowledge_outcomes LONGTEXT,
  skills_outcomes LONGTEXT,
  competence_outcomes LONGTEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  INDEX idx_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SQL Functions for Data Insertion (to be implemented in application)
-- ============================================================================

-- Function to insert study program
-- CALL insert_study_program(
--   'Administrativ koordinator',
--   'Description here...',
--   60,
--   'Norsk',
--   'Fagskolegrad',
--   ...
-- );

-- Function to insert course with learning outcomes
-- CALL insert_course_with_outcomes(
--   study_program_id,
--   'Course Title',
--   '10 studiepoeng',
--   'Fagskolegrad',
--   'url_here',
--   'Knowledge outcomes...',
--   'Skills outcomes...',
--   'Competence outcomes...'
-- );
