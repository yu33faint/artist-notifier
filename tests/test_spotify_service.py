from unittest.mock import MagicMock, patch

from backend.app.services.spotify import search_artist


def test_search_artist_returns_artist_when_found():
    fake_response = {
        "artists": {
            "items" : [
                {"id": "abc123", "name": "Vaundy"}
            ]
        }
    }
    fake_spotify_client = MagicMock()
    fake_spotify_client.search.return_value = fake_response

    with patch("backend.app.services.spotify.get_spotify_client", return_value=fake_spotify_client):
        result = search_artist("Vaundy")

    assert result == {"id": "abc123", "name": "Vaundy"}


def test_search_artist_returns_none_when_not_found():
    fake_response = {"artists": {"items": []}}
    fake_spotify_client = MagicMock()
    fake_spotify_client.search.return_value = fake_response

    with patch("backend.app.services.spotify.get_spotify_client", return_value=fake_spotify_client):
        result = search_artist("存在しないはずのアーティスト12345")

    assert result is None
