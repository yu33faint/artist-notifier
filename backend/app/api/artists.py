import sqlite3

from fastapi import APIRouter

from backend.app.database import get_db_connection
from backend.app.schemas.artist import ArtistRequest
from backend.app.services.spotify import search_artist
from backend.app.repositories.artists import get_all_artists


router = APIRouter(prefix="/api", tags=["artists"])

@router.post("/register")
def register_artist(req: ArtistRequest):
    try:
        artist = search_artist(req.artist_name)
    except Exception as error:
        return {
            "status": "error",
            "message": f"Spotify検索エラー: {error}"
        }
    if artist is None:
        return {
            "status": "error",
            "message": f"「{req.artist_name}」が見つかりませんでした。"
        }
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO artists (id, name) VALUES (?, ?)", (artist["id"], artist["name"]))
        conn.commit()
        message = f"「{artist['name']}」を監視リストに追加しました。"
    except sqlite3.IntegrityError:
        message = f"「{artist['name']}」は既に監視リストに登録されています。"
    finally:
        conn.close()

    return {
        "status": "success",
        "message": message
    }

@router.get("/artists")
def get_artists():
    return {
        "status": "success",
        "artists": get_all_artists(),
    }

@router.delete("/artists/{artist_id}")
def delete_artist(artist_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM artists WHERE id = ?",
            (artist_id,)
        )
        conn.commit()
        deleted_count = cursor.rowcount
    finally:
        conn.close()

    if deleted_count == 0:
        return {
            "status": "error",
            "message": "指定されたアーティストは登録されていません。"
        }
    else:
        return {
            "status": "success",
            "message": "アーティストを監視リストから削除しました。"
        }