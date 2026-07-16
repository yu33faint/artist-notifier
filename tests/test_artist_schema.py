import pytest
from pydantic import ValidationError

from backend.app.schemas.artist import ArtistRequest


def test_artist_request_accepts_valid_name():
    request = ArtistRequest(artist_name="Vaundy")
    assert request.artist_name == "Vaundy"


def test_artist_request_rejects_missing_name():
    with pytest.raises(ValidationError):
        ArtistRequest()
