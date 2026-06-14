from backend.app.database import get_db_connection

def get_all_artists():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, name FROM artists")
        return [
            {
                "id": row[0],
                "name": row[1]
            }
            for row in cursor.fetchall()
        ]
    finally:
        conn.close()