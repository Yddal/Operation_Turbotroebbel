from db import get_connection


def fetch_studieformer() -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT navn FROM studieformer ORDER BY navn"
        )
        rows = cursor.fetchall()
        cursor.close()
        print("Rows fetched:", rows )
        return rows
    finally:
        conn.close()
