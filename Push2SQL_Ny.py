"""
Load JSON files from the `json_for_processing` folder and push data
into the MySQL database schema defined in `e-l/databasesetup.sql`.

Behavior:
- Loops all .json files in `json_for_processing` next to this script.
- Inserts/updates `courses`, `study_place`, `study_programs`, and
  `lookuptalbe_study_course` tables.
- Deduplicates locations and courses.

Usage:
  python push2sql_ny.py --config path/to/config.cnf

Config file (optional): will try these defaults relative to this script:
  - e-l/config.cnf
  - config.cnf

If `mysql-connector-python` is not installed, install with:
  pip install mysql-connector-python
"""

from __future__ import annotations

import argparse
import configparser
import json
import os
import sys
from glob import glob
from typing import Dict, Any, List, Optional, Tuple

try:
    import mysql.connector
    from mysql.connector import errorcode
except Exception as e:  # pragma: no cover - user will install if missing
    print("Missing mysql connector. Install with: pip install mysql-connector-python")
    raise

HOSTNAME = "127.0.0.1"
USERNAME = "root"
PASSWORD = "admin"

def find_config_candidates(base_dir: str) -> List[str]:
    return [
        os.path.join(base_dir, "config.cnf"),
    ]


def read_db_config(path: Optional[str], base_dir: str) -> Dict[str, str]:
    cfg = configparser.ConfigParser()
    candidates = [] if path else find_config_candidates(base_dir)
    if path:
        candidates = [path]

    read = cfg.read(candidates)
    if not read and not path:
        return {}

    section = "mysql"
    if section not in cfg:
        # allow generic [client] or [database]
        for alt in ("client", "database"):
            if alt in cfg:
                section = alt
                break

    if section not in cfg:
        return {}

    conf = cfg[section]
    return {
        "host": conf.get("host", HOSTNAME),
        "user": conf.get("user", conf.get("username", USERNAME)),
        "password": conf.get("password", PASSWORD),
        "database": conf.get("database", conf.get("db", "fagskolen")),
        "port": conf.get("port", "3306"),
    }


def connect_db(conf: Dict[str, str]):
    return mysql.connector.connect(
        host=conf.get("host", HOSTNAME),
        user=conf.get("user", USERNAME),
        password=conf.get("password", PASSWORD),
        database=conf.get("database", "fagskolen"),
        port=int(conf.get("port", 3306)),
        autocommit=False,
    )


def load_json_files(folder: str) -> List[str]:
    pattern = os.path.join(folder, "*.json")
    return sorted(glob(pattern))


def ensure_location(cursor, name: str, existing: Dict[str, int], next_id_ref: List[int]) -> int:
    # return existing id or insert a new one
    if not name:
        return None
    key = name.strip()
    if key in existing:
        return existing[key]

    new_id = next_id_ref[0]
    cursor.execute(
        "INSERT INTO study_place (location_id, location_name) VALUES (%s, %s)",
        (new_id, key),
    )
    existing[key] = new_id
    next_id_ref[0] += 1
    return new_id


def upsert_course(cursor, course: Dict[str, Any]):
    sql = (
        "INSERT INTO courses (course_id, course_title, credits, url, study_level, lear_out_know, lear_out_skills, lear_out_competence) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) "
        "ON DUPLICATE KEY UPDATE course_title=VALUES(course_title), credits=VALUES(credits), url=VALUES(url), study_level=VALUES(study_level), "
        "lear_out_know=VALUES(lear_out_know), lear_out_skills=VALUES(lear_out_skills), lear_out_competence=VALUES(lear_out_competence)"
    )
    learning = course.get("learning_outcomes", {})
    know = learning.get("knowledge") if isinstance(learning, dict) else None
    skills = learning.get("skills") if isinstance(learning, dict) else None
    comp = learning.get("competence") if isinstance(learning, dict) else None
    cursor.execute(
        sql,
        (
            course.get("id"),
            course.get("title"),
            float(course.get("credits")) if course.get("credits") is not None else None,
            course.get("url"),
            course.get("study_level"),
            know,
            skills,
            comp,
        ),
    )


def upsert_study_program(cursor, program: Dict[str, Any], location_id: Optional[int]):
    sql = (
        "INSERT INTO study_programs (study_id, study_title, study_description, location_id, credits, study_language, study_lvl, why_choose, what_learn, teaching_format, mandatory_attendance, police_certificate, career_opportunities, contact_info, study_url, course_id) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
        "ON DUPLICATE KEY UPDATE study_title=VALUES(study_title), study_description=VALUES(study_description), location_id=VALUES(location_id), credits=VALUES(credits), study_language=VALUES(study_language), study_lvl=VALUES(study_lvl), why_choose=VALUES(why_choose), what_learn=VALUES(what_learn), teaching_format=VALUES(teaching_format), mandatory_attendance=VALUES(mandatory_attendance), police_certificate=VALUES(police_certificate), career_opportunities=VALUES(career_opportunities), contact_info=VALUES(contact_info), study_url=VALUES(study_url), course_id=VALUES(course_id)"
    )

    police = program.get("police_certificate")
    if police is None:
        police_val = None
    else:
        police_val = bool(police)

    cursor.execute(
        sql,
        (
            program.get("id"),
            program.get("title"),
            program.get("description"),
            location_id,
            float(program.get("credits")) if program.get("credits") is not None else None,
            program.get("language"),
            program.get("level"),
            program.get("why_choose"),
            program.get("what_learn"),
            program.get("teaching_format"),
            program.get("mandatory_attendance"),
            police_val,
            program.get("career_opportunities"),
            program.get("contact_info"),
            program.get("study_url"),
            None,
        ),
    )


def insert_lookup(cursor, study_id: str, course_id: str):
    cursor.execute(
        "INSERT IGNORE INTO lookuptalbe_study_course (study_id, course_id) VALUES (%s, %s)",
        (study_id, course_id),
    )


def main(argv: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(description="Push JSON files to MySQL fagskolen DB")
    parser.add_argument("--config", help="path to config.cnf (optional)")
    parser.add_argument("--folder", help="json_for_processing folder", default=os.path.join(os.path.dirname(__file__), "json_for_processing"))
    parser.add_argument("--dry-run", action="store_true", help="Parse only, don't write to DB")
    args = parser.parse_args(argv)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_conf = read_db_config(args.config, base_dir)
    if not db_conf:
        print("No config found. Provide --config or create e-l/config.cnf with [mysql] section.")
        print("Attempting default local connection to database 'fagskolen' on localhost.")
        db_conf = {"host": HOSTNAME, "user":USERNAME, "password": PASSWORD, "database": "fagskolen", "port": "3306"}

    files = load_json_files(args.folder)
    if not files:
        print("No JSON files found in:", args.folder)
        return

    conn = None
    cur = None
    try:
        if not args.dry_run:
            conn = connect_db(db_conf)
            cur = conn.cursor()

            # load existing locations
            cur.execute("SELECT location_id, location_name FROM study_place")
            existing_locations: Dict[str, int] = {r[1]: int(r[0]) for r in cur.fetchall()}
            cur.execute("SELECT COALESCE(MAX(location_id),0) FROM study_place")
            row = cur.fetchone()
            next_loc = int(row[0]) + 1 if row else 1
            next_id_ref = [next_loc]
        else:
            existing_locations = {}
            next_id_ref = [1]

        for path in files:
            print("Processing:", path)
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)

            courses = data.get("courses", []) or []
            programs = data.get("study_programs", []) or []

            # Upsert courses
            for c in courses:
                cid = c.get("id")
                print("  Course:", cid)
                if not cid:
                    # skip malformed course entries without id
                    continue
                if not args.dry_run:
                    upsert_course(cur, c)

            # For each program, ensure location, insert program, then link to all courses in file
            for p in programs:
                loc_name = p.get("study_location") or p.get("location")
                # normalize location value: allow string, dict, or list
                if isinstance(loc_name, dict):
                    loc_name = loc_name.get("name") or loc_name.get("location") or next(iter(loc_name.values()), None)
                if isinstance(loc_name, list):
                    loc_name = ", ".join(str(x) for x in loc_name)
                loc_id = None
                if loc_name:
                    if args.dry_run:
                        # simulate id assignment
                        if loc_name not in existing_locations:
                            existing_locations[loc_name] = next_id_ref[0]
                            next_id_ref[0] += 1
                        loc_id = existing_locations[loc_name]
                    else:
                        # ensure in DB
                        loc_id = ensure_location(cur, loc_name, existing_locations, next_id_ref)

                print("  Program:", p.get("id"), "-> location_id", loc_id)
                if not args.dry_run:
                    upsert_study_program(cur, p, loc_id)

                # create lookup rows between this program and all courses in file
                for c in courses:
                    if not c.get("id"):
                        continue
                    if not args.dry_run:
                        insert_lookup(cur, p.get("id"), c.get("id"))

        if not args.dry_run and conn:
            conn.commit()
            print("Committed changes to database.")
        else:
            print("Dry run complete; no changes written.")

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        print(f"MySQL error: {err}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
