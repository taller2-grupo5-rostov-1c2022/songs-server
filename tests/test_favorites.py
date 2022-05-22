from tests.utils import (
    post_user,
    post_song,
    post_album,
    add_song_to_favorites,
    block_song,
    get_favorite_songs,
    delete_song_from_favorites,
)
from tests.utils import API_VERSION_PREFIX


def test_get_favorite_songs_with_zero_favorite_songs(client):
    post_user(client, "user_id", "user_name")
    response_get = client.get(
        f"{API_VERSION_PREFIX}/users/user_id/favorites/songs",
        headers={
            "api_key": "key",
            "uid": "user_id",
        },
    )
    assert response_get.status_code == 200
    assert response_get.json() == []


def test_get_favorite_songs_with_one_favorite_songs(client):
    post_user(client, "user_id", "user_name")
    song_id = post_song(client, uid="user_id").json()["id"]
    response_post = add_song_to_favorites(client, uid="user_id", song_id=song_id)
    assert response_post.status_code == 200

    response_get = get_favorite_songs(client, uid="user_id")

    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_name"


def test_get_favorite_songs_with_two_favorite_songs(client):
    post_user(client, "user_id", "user_name")
    song_id_1 = post_song(client, name="first_song", uid="user_id").json()["id"]
    song_id_2 = post_song(client, name="second_song", uid="user_id").json()["id"]
    response_post = add_song_to_favorites(client, uid="user_id", song_id=song_id_1)
    assert response_post.status_code == 200
    response_post = add_song_to_favorites(client, uid="user_id", song_id=song_id_2)
    assert response_post.status_code == 200

    response_get = get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 2
    assert songs[0]["name"] == "first_song"
    assert songs[1]["name"] == "second_song"


def test_get_favorite_songs_only_returns_favorite_songs(client):
    post_user(client, "user_id", "user_name")
    song_id_1 = post_song(client, name="first_song", uid="user_id").json()["id"]
    post_song(client, name="second_song", uid="user_id")

    add_song_to_favorites(client, uid="user_id", song_id=song_id_1)
    response_get = get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "first_song"


def test_get_favorite_songs_with_blocked_song(client):
    post_user(client, "user_id", "user_name")
    song_id_1 = post_song(client, name="first_song", uid="user_id").json()["id"]
    song_id_2 = post_song(client, name="second_song", uid="user_id").json()["id"]
    response_post = add_song_to_favorites(client, uid="user_id", song_id=song_id_1)
    assert response_post.status_code == 200
    response_post = add_song_to_favorites(client, uid="user_id", song_id=song_id_2)
    assert response_post.status_code == 200
    block_song(client, id=song_id_1)

    response_get = get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "second_song"


def test_remove_song_from_favorites(client):
    post_user(client, "user_id", "user_name")
    song_id = post_song(client, uid="user_id").json()["id"]
    response_post = add_song_to_favorites(client, uid="user_id", song_id=song_id)
    assert response_post.status_code == 200

    response_get = get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_name"

    response_delete = delete_song_from_favorites(client, uid="user_id", song_id=song_id)
    assert response_delete.status_code == 200

    response_get = get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 0


def test_remove_song_from_favorites_removes_only_expected_song(client):
    post_user(client, "user_id", "user_name")
    song_id_1 = post_song(client, name="first_song", uid="user_id").json()["id"]
    song_id_2 = post_song(client, name="second_song", uid="user_id").json()["id"]
    add_song_to_favorites(client, uid="user_id", song_id=song_id_1)
    add_song_to_favorites(client, uid="user_id", song_id=song_id_2)

    response_delete = delete_song_from_favorites(client, uid="user_id", song_id=song_id_1)
    assert response_delete.status_code == 200

    response_get = get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["id"] == song_id_2
    assert songs[0]["name"] == "second_song"


def test_user_cann_add_to_favorites_songs_of_another_user(client):
    post_user(client, "creator_id", "creator_name")
    post_user(client, "listener_id", "listener_name")
    song_id = post_song(client, name="song_by_creator", uid="creator_id").json()["id"]

    add_song_to_favorites(client, uid="listener_id", song_id=song_id)
    response_get = get_favorite_songs(client, uid="listener_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["id"] == song_id
    assert songs[0]["name"] == "song_by_creator"


def test_get_favorite_albums_with_zero_favorite_albums(client):
    post_user(client, "user_id", "user_name")
    response_get = get_favorite_albums(client, uid="user_id")
    albums = response_get.json()

    assert response_get.status_code == 200
    assert len(albums) == 0


