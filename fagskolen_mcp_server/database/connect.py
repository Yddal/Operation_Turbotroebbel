import os

import mysql.connector


def main() -> None:
    config_path = os.path.join(os.path.dirname(__file__), "config.cnf")
    conn = mysql.connector.connect(
        option_files=config_path,
        option_groups="client",
    )
    conn.ping(reconnect=True, attempts=1, delay=0)
    print("Connection OK")
    conn.close()


if __name__ == "__main__":
    main()

