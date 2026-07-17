from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.repositories.artists import create_artist

client = TestClient(app)


def test_register_artist_success(use_test_database):
    fake_response = {
        "artists": {"items": [{"id": "artist-1", "name": "Vaundy"}]}
    }
    fake_spotify_client = MagicMock()
    fake_spotify_client.search.return_value = fake_response

    with patch("backend.app.services.spotify.get_spotify_client", return_value=fake_spotify_client):
        response = client.post("/api/register", json={"artist_name": "Vaundy"})

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_register_artist_not_found(use_test_database):
    fake_response = {"artists": {"items": []}}
    fake_spotify_client = MagicMock()
    fake_spotify_client.search.return_value = fake_response

    with patch("backend.app.services.spotify.get_spotify_client", return_value=fake_spotify_client):
        response = client.post("/api/register", json={"artist_name": "存在しないはず"})

    assert response.status_code == 404
    assert "見つかりませんでした" in response.json()["detail"]


def test_get_artists_returns_registered_artists(use_test_database):
    create_artist("artist-1", "Vaundy")

    response = client.get("/api/artists")

    assert response.status_code == 200
    assert response.json()["artists"] == [{"id": "artist-1", "name": "Vaundy"}]


def test_delete_artist_success(use_test_database):
    create_artist("artist-1", "Vaundy")

    response = client.delete("/api/artists/artist-1")

    assert response.status_code == 200


def test_delete_artist_not_found(use_test_database):
    response = client.delete("/api/artists/does-not-exist")

    assert response.status_code == 404
