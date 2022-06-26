import time

from tests import utils
from tests.utils import post_song, post_user, post_album
from tests.utils import API_VERSION_PREFIX
from urllib.parse import urlparse
from urllib.parse import parse_qs


def test_unauthorized_get(client, custom_requests_mock):
    response = client.get(API_VERSION_PREFIX + "/songs/")
    assert response.status_code == 403


def test_get_songs(client, custom_requests_mock):
    response = client.get(API_VERSION_PREFIX + "/songs/", headers={"api_key": "key"})
    assert response.status_code == 200


def test_post_song(client, custom_requests_mock):
    post_user(client, "song_creator_id")
    response_post = post_song(client, unwrap_id=False)
    assert response_post.status_code == 200
    song_id = response_post.json()["id"]

    song = utils.get_song(client, song_id, "song_creator_id", unwrap=True)

    assert song["id"] == song_id
    assert song["name"] == "song_name"
    assert song["description"] == "song_desc"
    assert song["artists"] == [{"name": "song_artist_name"}]
    assert song["genre"] == "song_genre"
    assert song["sub_level"] == 0
    assert song["file"].startswith("https://example.com")
    assert song["album"] is None


def test_cannot_post_song_with_not_created_user(client, custom_requests_mock):
    response_post = post_song(client, uid="not_created_user_id", unwrap_id=False)
    assert response_post.status_code == 404


def test_put_song(client, custom_requests_mock):
    post_user(client, "song_creator_id", "song_creator")
    song_id = post_song(client)

    response_put = utils.put_song(
        client,
        song_id,
        {"name": "updated_test_song", "artists": '["updated_test_artists"]'},
    )
    assert response_put.status_code == 200

    song = utils.get_song(client, song_id, uid="song_creator_id", unwrap=True)

    assert str(song["id"]) == str(song_id)
    assert song["name"] == "updated_test_song"
    assert song["description"] == "song_desc"
    assert song["artists"] == [{"name": "updated_test_artists"}]


def test_cannot_put_song_of_another_user(client, custom_requests_mock):
    utils.post_users(client, "song_creator_id", "another_creator_id")

    song_id = post_song(client, uid="song_creator_id")

    response_update = utils.put_song(
        client, song_id, {"name": "updated_test_song"}, uid="another_creator_id"
    )

    assert response_update.status_code == 403


def test_get_song_by_creator(client, custom_requests_mock):
    utils.post_users(client, "song_creator_id", "another_creator_id")

    for i in range(3):
        response_post = utils.post_song(
            client, uid="song_creator_id", name=f"song_{i}", unwrap_id=False
        )
        assert response_post.status_code == 200

    for i in range(3):
        response_post = utils.post_song(
            client, uid="another_creator_id", name=f"song_another_{i}", unwrap_id=False
        )
        assert response_post.status_code == 200

    songs = utils.get_songs_by_creator(client, "song_creator_id", unwrap=True)

    assert len(songs) == 3
    for i, song in enumerate(songs):
        assert song["name"] == f"song_{i}"


def test_delete_song(client, custom_requests_mock):
    post_user(client, "song_creator_id")
    response_post = post_song(client, unwrap_id=False)
    assert response_post.status_code == 200
    song_id = response_post.json()["id"]

    response_delete = utils.delete_song(client, song_id)

    assert response_delete.status_code == 200

    response_get = utils.get_song(client, song_id)

    assert response_get.status_code == 404


def test_cannot_delete_song_of_another_user(client, custom_requests_mock):
    utils.post_users(client, "song_creator_id", "another_creator_id")
    song_id = post_song(client, uid="song_creator_id")
    response_delete = utils.delete_song(client, song_id, uid="another_creator_id")

    assert response_delete.status_code == 403


def test_cannot_delete_song_that_does_not_exist(client, custom_requests_mock):
    post_user(client, "song_creator_id")

    response_delete = utils.delete_song(client, 1, uid="song_creator_id")

    assert response_delete.status_code == 404


def test_get_my_songs_without_results(client, custom_requests_mock):
    post_user(client, "song_creator_id", "song_creator")
    post_user(client, "another_creator_id", "another_creator")

    post_song(client, uid="another_creator_id", name="happy_song")

    response_get = utils.get_my_songs(
        client, uid="song_creator_id"
    )
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 0


def test_get_my_songs_should_retrieve_two_songs(client, custom_requests_mock):
    post_user(client, "song_creator_id", "song_creator")
    post_song(client, uid="song_creator_id", name="happy_song")
    post_song(client, uid="song_creator_id", name="sad_song")

    response_get = utils.get_my_songs(
        client, uid="song_creator_id"
    )

    body_songs = response_get.json()

    assert response_get.status_code == 200
    assert len(body_songs) == 2
    assert body_songs[0]["name"] == "happy_song"
    assert body_songs[0]["artists"] == [{"name": "song_artist_name"}]
    assert body_songs[1]["name"] == "sad_song"


def test_post_with_invalid_artists_format_should_fail(client, custom_requests_mock):
    post_user(client, "song_creator_id", "song_creator")

    with open("./tests/test.song", "wb") as f:
        f.write(b"test")
    with open("./tests/test.song", "rb") as f:
        response_post = client.post(
            API_VERSION_PREFIX + "/songs/",
            data={
                "name": "test_song",
                "description": "test_desc",
                "artists": "invalid artists format",
                "genre": "test_genre",
            },
            files={"file": ("song.txt", f, "plain/text")},
            headers={"uid": "song_creator_id", "api_key": "key", "role": "artist"},
        )

    assert response_post.status_code == 422


def test_update_song_updates_song_timestamp(client, custom_requests_mock):
    post_user(client, "song_creator_id")
    song_id = post_song(client, uid="song_creator_id")

    response_get_1 = utils.get_song(client, song_id)

    time.sleep(1)
    with open("./new_song.img", "wb") as f:
        f.write(b"song info")
    with open("./new_song.img", "rb") as f:
        response_put = client.put(
            f"{API_VERSION_PREFIX}/songs/{song_id}",
            files={"file": ("new_song.img", f, "plain/text")},
            headers={"uid": "song_creator_id", "api_key": "key"},
        )
        assert response_put.status_code == 200

    response_get_2 = utils.get_song(client, song_id)

    url_1 = response_get_1.json()["file"]
    url_2 = response_get_2.json()["file"]

    timestamp_1 = parse_qs(urlparse(url_1).query)["t"][0]
    timestamp_2 = parse_qs(urlparse(url_2).query)["t"][0]

    assert timestamp_1 != timestamp_2


def test_listener_cannot_post_song(client, custom_requests_mock):
    post_user(client, "listener_id")
    response_post = post_song(
        client, uid="listener_id", role="listener", unwrap_id=False
    )

    assert response_post.status_code == 403


def test_admin_can_delete_song_of_another_user(client, custom_requests_mock):
    utils.post_users(client, "song_creator_id", "admin_id")
    song_id = post_song(client)
    response_delete = utils.delete_song(client, song_id, uid="admin_id", role="admin")

    assert response_delete.status_code == 200


def test_admin_can_edit_song_of_another_user(client, custom_requests_mock):
    utils.post_users(client, "song_creator_id", "admin_id")

    song_id = post_song(client)
    response_put = utils.put_song(
        client, song_id, {"name": "new_name"}, uid="admin_id", role="admin"
    )

    assert response_put.status_code == 200


def test_post_song_with_album(client, custom_requests_mock):
    post_user(client, "song_creator_id")
    album_id = post_album(client)
    song_id = post_song(client, album_id=album_id)

    response = utils.get_song(client, song_id)
    song = response.json()

    assert response.status_code == 200
    assert song["album"]["id"] == album_id
