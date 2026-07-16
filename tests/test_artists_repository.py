from backend.app.repositories.artists import (
    create_artist,
    delete_artist_by_id,
    get_all_artist_records,
    get_all_artists,
)


def test_create_artist_adds_new_artist(use_test_database):
    was_created = create_artist("artist-1", "Vaundy")

    assert was_created is True
    assert get_all_artists() == [{"id": "artist-1", "name": "Vaundy"}]


def test_create_artist_rejects_duplicate_id(use_test_database):
    create_artist("artist-1", "Vaundy")
    was_created_again = create_artist("artist-1", "Vaundy")

    assert was_created_again is False
    assert len(get_all_artists()) == 1


def test_delete_artist_by_id_removes_existing_artist(use_test_database):
    create_artist("artist-1", "Vaundy")

    was_deleted = delete_artist_by_id("artist-1")

    assert was_deleted is True
    assert get_all_artists() == []


def test_delete_artist_by_id_returns_false_when_not_found(use_test_database):
    was_deleted = delete_artist_by_id("does-not-exist")

    assert was_deleted is False


def test_get_all_artist_records_returns_tuples(use_test_database):
    create_artist("artist-1", "Vaundy")

    records = get_all_artist_records()

    assert records == [("artist-1", "Vaundy")]
