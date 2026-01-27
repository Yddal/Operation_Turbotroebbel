-- 01_create_tables_mysql.sql
-- Database: studie-fokusert modell (MySQL 8.x)

CREATE DATABASE IF NOT EXISTS fagskolen
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE fagskolen;

CREATE TABLE IF NOT EXISTS studiesteder (
  studiested_id INT AUTO_INCREMENT PRIMARY KEY,
  navn          VARCHAR(120) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS studieformer (
  studieform_id INT AUTO_INCREMENT PRIMARY KEY,
  navn          VARCHAR(120) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS studieprogram (
  studieprogram_id INT AUTO_INCREMENT PRIMARY KEY,
  navn             VARCHAR(200) NOT NULL UNIQUE,
  kategori         VARCHAR(80)  NOT NULL DEFAULT 'Helse',
  program_url      TEXT,
  kort_beskrivelse TEXT
) ENGINE=InnoDB;

-- Ett program kan ha mange "tilbud" (varianter) per studiested, varighet, studieform osv.
CREATE TABLE IF NOT EXISTS studietilbud (
  studietilbud_id  INT AUTO_INCREMENT PRIMARY KEY,

  studieprogram_id INT NOT NULL,
  studiested_id    INT NOT NULL,
  studieform_id    INT NOT NULL,

  -- Varighet lagres fleksibelt (f.eks. 2 år, 12 uker, 1 år)
  varighet_verdi   INT NOT NULL,
  varighet_enhet   VARCHAR(20) NOT NULL,

  -- Noen tilbud har intervall (f.eks. 10-60, 25-30). Da bruker vi min/max.
  studiepoeng_min  DECIMAL(5,1) NOT NULL,
  studiepoeng_max  DECIMAL(5,1) NOT NULL,

  -- Opptak / status (enkelt, kan utvides senere)
  apent_for_opptak TINYINT(1) NOT NULL DEFAULT 1,
  merknad          TEXT,

  CONSTRAINT fk_tilbud_program
    FOREIGN KEY (studieprogram_id) REFERENCES studieprogram(studieprogram_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_tilbud_sted
    FOREIGN KEY (studiested_id) REFERENCES studiesteder(studiested_id),
  CONSTRAINT fk_tilbud_form
    FOREIGN KEY (studieform_id) REFERENCES studieformer(studieform_id),

  CONSTRAINT uq_tilbud UNIQUE (
    studieprogram_id, studiested_id, studieform_id,
    varighet_verdi, varighet_enhet, studiepoeng_min, studiepoeng_max
  ),

  CONSTRAINT ck_varighet_verdi CHECK (varighet_verdi > 0),
  CONSTRAINT ck_varighet_enhet CHECK (varighet_enhet IN ('uker','måneder','år')),
  CONSTRAINT ck_studiepoeng_min CHECK (studiepoeng_min >= 0),
  CONSTRAINT ck_studiepoeng_max CHECK (studiepoeng_max >= studiepoeng_min)
) ENGINE=InnoDB;

-- Valgfritt (men nyttig for undervisning): emner/moduler per program
CREATE TABLE IF NOT EXISTS emner (
  emne_id          INT AUTO_INCREMENT PRIMARY KEY,
  studieprogram_id INT NOT NULL,
  emnenavn         VARCHAR(200) NOT NULL,
  emnekode         VARCHAR(50),
  studiepoeng      DECIMAL(5,1),
  rekkefolge       INT,
  kort_beskrivelse TEXT,
  CONSTRAINT fk_emner_program
    FOREIGN KEY (studieprogram_id) REFERENCES studieprogram(studieprogram_id)
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- Valgfritt (men nyttig): læreplan/studieplan-lenker og versjonering
CREATE TABLE IF NOT EXISTS studieplaner (
  studieplan_id    INT AUTO_INCREMENT PRIMARY KEY,
  studieprogram_id INT NOT NULL,
  plan_url         TEXT NOT NULL,
  gyldig_fra       DATE,
  merknad          TEXT,
  CONSTRAINT fk_planer_program
    FOREIGN KEY (studieprogram_id) REFERENCES studieprogram(studieprogram_id)
    ON DELETE CASCADE
) ENGINE=InnoDB;
