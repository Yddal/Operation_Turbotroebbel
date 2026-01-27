import os

import mysql.connector


def run_sql_file(cursor: mysql.connector.cursor.MySQLCursor, path: str) -> None:
    with open(path, "r", encoding="utf-8") as handle:
        sql_lines = handle.readlines()

    statements = []
    buffer = []
    for line in sql_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("--") or stripped.startswith("#"):
            continue
        buffer.append(line)
        if ";" in line:
            joined = "".join(buffer)
            parts = joined.split(";")
            for part in parts[:-1]:
                stmt = part.strip()
                if stmt:
                    statements.append(stmt)
            buffer = [parts[-1]]

    trailing = "".join(buffer).strip()
    if trailing:
        statements.append(trailing)

    for statement in statements:
        cursor.execute(statement)


def main() -> None:
    base_dir = os.path.dirname(__file__)
    config_path = os.path.join(base_dir, "config.cnf")
    create_sql = os.path.join(base_dir, "01_create_tables_mysql.sql")
    seed_sql = os.path.join(base_dir, "02_seed_data_mysql.sql")

    conn = mysql.connector.connect(
        option_files=config_path,
        option_groups="client",
        database=None,
        use_pure=True,
    )
    conn.autocommit = False

    cursor = conn.cursor()
    run_sql_file(cursor, create_sql)
    run_sql_file(cursor, seed_sql)
    conn.commit()

    cursor.close()
    conn.close()
    print("Database setup complete.")


if __name__ == "__main__":
    main()
