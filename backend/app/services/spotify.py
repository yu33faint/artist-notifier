import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_spotify_client():
    manager = SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
    )
    return spotipy.Spotify(client_credentials_manager=manager)

def search_artist(artist_name: str):
    spotify = get_spotify_client()
    result = spotify.search(q=artist_name, type="artist", limit=1)
    artists = result["artists"]["items"]

    if not artists:
        return None

    artist = artists[0]

    return {
        "id": artist["id"],
        "name": artist["name"],
    }