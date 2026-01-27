import os

import mysql.connector


def get_connection() -> mysql.connector.MySQLConnection:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, "database", "config.cnf")
    return mysql.connector.connect(
        option_files=config_path,
        option_groups="client",
    )

