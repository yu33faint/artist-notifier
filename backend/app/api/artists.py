from fastapi import APIRouter, HTTPException

from backend.app.schemas.artist import ArtistRequest
from backend.app.services.spotify import search_artist
from backend.app.repositories.artists import (get_all_artists,
                                              create_artist,
                                              delete_artist_by_id)


router = APIRouter(prefix="/api", tags=["artists"])

@router.post("/register")
def register_artist(req: ArtistRequest):
    try:
        artist = search_artist(req.artist_name)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Spotify検索エラー: {error}")
    if artist is None:
        raise HTTPException(status_code=404, detail=f"「{req.artist_name}」が見つかりませんでした。")

    was_created = create_artist(artist["id"], artist["name"])

    if was_created:
        message = f"「{artist['name']}」を監視リストに登録しました。"
    else:
        message = f"「{artist['name']}」は既に監視リストに登録されています。"

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
    was_deleted = delete_artist_by_id(artist_id)

    if not was_deleted:
        raise HTTPException(status_code=404, detail="指定されたアーティストは登録されていません。")

    return {
        "status": "success",
        "message": "アーティストを監視リストから削除しました。"
    }
