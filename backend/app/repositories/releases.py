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

def save_releases(releases: list[tuple[str, str, str]],) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.executemany(
            "INSERT INTO releases (id, name, artist) VALUES (?, ?, ?)",
            releases,
        )
        conn.commit()
    finally:
        conn.close()