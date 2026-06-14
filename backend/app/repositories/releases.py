from backend.app.database import get_db_connection

def get_all_release_ids() -> set[str]:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM releases")
        return {
            row[0]
            for row in cursor.fetchall()
        }
    finally:
        conn.close()
