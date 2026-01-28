import os
import json
import argparse
from glob import glob
from typing import Dict, Any

import mysql.connector
from mysql.connector import errors as mysql_errors
try:
	import pymysql
except Exception:
	pymysql = None


def connect_db(host, user, password, database):
	# Prefer pymysql (more flexible auth) when available
	if pymysql is not None:
		return pymysql.connect(host=host, user=user, password=password, database=database, autocommit=False)
	return mysql.connector.connect(host=host, user=user, password=password, database=database, autocommit=False)


def upsert_course(cursor, course: Dict[str, Any]):
	sql = ("INSERT INTO courses (course_id, course_title, credits, url, study_level, lear_out_know, lear_out_skills, lear_out_competence)"
		   " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
		   " ON DUPLICATE KEY UPDATE course_title=VALUES(course_title), credits=VALUES(credits), url=VALUES(url), study_level=VALUES(study_level),"
		   " lear_out_know=VALUES(lear_out_know), lear_out_skills=VALUES(lear_out_skills), lear_out_competence=VALUES(lear_out_competence)")

	learning = course.get('learning_outcomes', {})
	course_id = course.get('id')
	if not course_id:
		return
	params = (
		course_id,
		course.get('title'),
		course.get('credits'),
		course.get('url'),
		course.get('study_level'),
		learning.get('knowledge'),
		learning.get('skills'),
		learning.get('competence'),
	)
	cursor.execute(sql, params)


def upsert_study_place(cursor, location_id: int, location_name: str):
	sql = ("INSERT INTO study_place (location_id, location_name) VALUES (%s,%s)"
		   " ON DUPLICATE KEY UPDATE location_name=VALUES(location_name)")
	cursor.execute(sql, (location_id, location_name))


def collect_all_locations(files: list) -> dict:
	"""Scan all JSON files and collect unique locations."""
	locations = {}
	for filepath in files:
		try:
			with open(filepath, 'r', encoding='utf-8') as f:
				data = json.load(f)
			for prog in data.get('study_programs', []):
				loc = prog.get('study_location') or {}
				if isinstance(loc, dict):
					for loc_key, loc_name in loc.items():
						try:
							loc_id = int(loc_key)
							if loc_id not in locations and loc_name:
								locations[loc_id] = loc_name
						except (ValueError, TypeError):
							pass
		except Exception:
			pass
	return locations


def upsert_study_program(cursor, program: Dict[str, Any], location_id: int):
	sql = ("INSERT INTO study_programs (study_id, study_title, study_description, study_category, location_id, credits, study_language, study_lvl, why_choose, what_learn, teaching_format, mandatory_attendance, police_certificate, career_opportunities, contact_info, study_url, course_id)"
		" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		" ON DUPLICATE KEY UPDATE study_title=VALUES(study_title), study_description=VALUES(study_description), study_category=VALUES(study_category), location_id=VALUES(location_id), credits=VALUES(credits), study_language=VALUES(study_language), study_lvl=VALUES(study_lvl), why_choose=VALUES(why_choose), what_learn=VALUES(what_learn), teaching_format=VALUES(teaching_format), mandatory_attendance=VALUES(mandatory_attendance), police_certificate=VALUES(police_certificate), career_opportunities=VALUES(career_opportunities), contact_info=VALUES(contact_info), study_url=VALUES(study_url), course_id=VALUES(course_id)")

	params = (
		program.get('id'),
		program.get('title'),
		program.get('description'),
		program.get('study_category'),
		location_id,
		program.get('credits'),
		program.get('language'),
		program.get('level'),
		program.get('why_choose'),
		program.get('what_learn'),
		program.get('teaching_format'),
		program.get('mandatory_attendance'),
		# Coerce police_certificate to boolean when possible
		(lambda v: (v if isinstance(v, bool) else (True if str(v).strip().lower() in ('true','1','yes','ja') else (False if str(v).strip().lower() in ('false','0','no','nei') else None))))(program.get('police_certificate')),
		program.get('career_opportunities'),
		program.get('contact_info'),
		program.get('study_url'),
		None,
	)
	cursor.execute(sql, params)


def process_file(cursor, filepath: str):
	with open(filepath, 'r', encoding='utf-8') as f:
		data = json.load(f)

	# Insert courses first (if any)
	for course in data.get('courses', []):
		upsert_course(cursor, course)

	# Insert study_programs and study_place
	for prog in data.get('study_programs', []):
		# study_location is a dict with id->name (string keys)
		loc = prog.get('study_location') or {}
		if isinstance(loc, dict) and len(loc) > 0:
			# pick first mapping
			loc_key = next(iter(loc.keys()))
			try:
				location_id = int(loc_key)
			except Exception:
				location_id = None
			location_name = loc.get(loc_key)
			if location_id is not None and location_name:
				upsert_study_place(cursor, location_id, location_name)
		else:
			location_id = None

		upsert_study_program(cursor, prog, location_id)


def main():
	parser = argparse.ArgumentParser(description='Push JSON study data into MySQL')
	parser.add_argument('--host', default='127.0.0.1')
	parser.add_argument('--user', default='root')
	parser.add_argument('--password', default='admin')
	parser.add_argument('--database', default='fagskolen')
	parser.add_argument('--json-dir', default='json_for_processing')
	parser.add_argument('--dry-run', action='store_true')
	args = parser.parse_args()

	files = glob(os.path.join(args.json_dir, '*.json'))
	if not files:
		print('No JSON files found in', args.json_dir)
		return

	if args.dry_run:
		print('Dry run: will parse and show counts')
		total_courses = total_programs = 0
		for fp in files:
			with open(fp, 'r', encoding='utf-8') as f:
				d = json.load(f)
			total_courses += len(d.get('courses', []))
			total_programs += len(d.get('study_programs', []))
		print(f'Found {total_courses} courses and {total_programs} study_programs in {len(files)} files')
		return

	try:
		conn = connect_db(args.host, args.user, args.password, args.database)
	except Exception as e:
		errcode = getattr(e, 'errno', None)
		if errcode is None and getattr(e, 'args', None):
			try:
				errcode = e.args[0]
			except Exception:
				errcode = None
		if errcode == 1049:
			# Unknown database -> try to create it and reconnect
			created = False
			try:
				tmp = mysql.connector.connect(host=args.host, user=args.user, password=args.password, autocommit=True)
				tmp_cursor = tmp.cursor()
				tmp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {args.database}")
				tmp.close()
				created = True
			except Exception:
				if pymysql is not None:
					tmp = pymysql.connect(host=args.host, user=args.user, password=args.password, autocommit=True)
					tmp_cursor = tmp.cursor()
					tmp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {args.database}")
					tmp.close()
					created = True
			if not created:
				raise
			conn = connect_db(args.host, args.user, args.password, args.database)
		else:
			raise
	# Ensure schema exists: if SQL schema file present, execute it to create tables
	schema_path = os.path.join(os.path.dirname(__file__), 'TurbotroebbelSQL.sql')
	if os.path.exists(schema_path):
		with open(schema_path, 'r', encoding='utf-8') as sf:
			sql_text = sf.read()
		stmts = [s.strip() for s in sql_text.split(';') if s.strip()]
		for stmt in stmts:
			try:
				tmpc = conn.cursor()
				tmpc.execute(stmt)
				if hasattr(conn, 'commit'):
					conn.commit()
				tmpc.close()
			except Exception:
				pass
		# Ensure credits columns can hold typical values (e.g., 60, 120)
		try:
			tmpc = conn.cursor()
			tmpc.execute("ALTER TABLE courses MODIFY credits DECIMAL(6,2)")
			tmpc.execute("ALTER TABLE study_programs MODIFY credits DECIMAL(6,2)")
			if hasattr(conn, 'commit'):
				conn.commit()
			tmpc.close()
		except Exception:
			pass
		# Increase text capacity for learning outcomes and descriptions
		try:
			tmpc = conn.cursor()
			tmpc.execute("ALTER TABLE courses MODIFY lear_out_know TEXT")
			tmpc.execute("ALTER TABLE courses MODIFY lear_out_skills TEXT")
			tmpc.execute("ALTER TABLE courses MODIFY lear_out_competence TEXT")
			tmpc.execute("ALTER TABLE study_programs MODIFY study_description TEXT")
			tmpc.execute("ALTER TABLE study_programs MODIFY contact_info TEXT")
			tmpc.execute("ALTER TABLE study_programs MODIFY mandatory_attendance TEXT")
			tmpc.execute("ALTER TABLE study_programs MODIFY teaching_format TEXT")
			tmpc.execute("ALTER TABLE study_programs ADD COLUMN study_category VARCHAR(100)")
			# To increase course_id length we must drop the FK, alter both tables, then recreate the FK
			try:
				tmpc.execute("ALTER TABLE study_programs DROP FOREIGN KEY courseID_FK")
			except Exception:
				pass
			try:
				tmpc.execute("ALTER TABLE study_programs DROP INDEX courseID_FK")
			except Exception:
				pass
			try:
				tmpc.execute("ALTER TABLE courses MODIFY course_id VARCHAR(64) NOT NULL")
				tmpc.execute("ALTER TABLE study_programs MODIFY course_id VARCHAR(64) NULL")
				tmpc.execute("ALTER TABLE study_programs ADD INDEX courseID_FK (course_id)")
				tmpc.execute("ALTER TABLE study_programs ADD CONSTRAINT courseID_FK FOREIGN KEY (course_id) REFERENCES courses(course_id)")
			except Exception:
				pass
			if hasattr(conn, 'commit'):
				conn.commit()
			tmpc.close()
		except Exception:
			pass

	try:
		cursor = conn.cursor()
		# Pre-insert all locations to avoid losing them on transaction rollback
		print('Pre-loading locations from all files...')
		all_locations = collect_all_locations(files)
		for loc_id, loc_name in sorted(all_locations.items()):
			try:
				upsert_study_place(cursor, loc_id, loc_name)
			except Exception as e:
				print('Warning: error inserting location', loc_id, ':', e)
		conn.commit()
		print(f'Pre-loaded {len(all_locations)} unique locations')
		# Now process files
		for fp in files:
			print('Processing', fp)
			process_file(cursor, fp)
		conn.commit()
		print('Done — committed to database')
	except Exception as e:
		conn.rollback()
		print('Error occurred, rolled back. Error:', e)
	finally:
		conn.close()


if __name__ == '__main__':
	main()
