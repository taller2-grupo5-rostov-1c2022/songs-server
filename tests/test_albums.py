import time

from src.constants import STORAGE_PATH
from tests import utils
from tests.utils import post_user, post_song, post_album
from tests.utils import API_VERSION_PREFIX
from urllib.parse import urlparse
from urllib.parse import parse_qs


def test_unauthorized_get(client, custom_requests_mock):
    response = client.get(API_VERSION_PREFIX + "/albums/")
    assert response.status_code == 403


def test_get_albums(client, custom_requests_mock):
    response = client.get(API_VERSION_PREFIX + "/albums/", headers={"api_key": "key"})
    assert response.status_code == 200


def test_get_album_by_invalid_id(client, custom_requests_mock):
    post_user(client, "album_creator_id", "album_creator_name")

    response = client.get(
        API_VERSION_PREFIX + "/albums/5",
        headers={"api_key": "key", "uid": "album_creator_id"},
    )

    assert response.status_code == 404


def test_get_album_of_user_without_albums(client, custom_requests_mock):
    post_user(client, "album_creator_id", "album_creator_name")
    response = client.get(
        API_VERSION_PREFIX + "/my_albums/",
        headers={"uid": "album_creator_id", "api_key": "key"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_my_albums(client, custom_requests_mock):
    post_user(client, "album_creator_id")
    post_album(client)

    response = utils.get_my_albums(client, "album_creator_id")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_name"
    assert albums[0]["description"] == "album_desc"
    assert albums[0]["genre"] == "album_genre"
    assert albums[0]["songs"] == []
    assert len(albums) == 1


def test_get_my_albums_does_not_return_albums_of_other_users(
    client, custom_requests_mock
):
    post_user(client, "album_creator_id", "album_creator_name")
    post_user(client, "another_creator_id", "another_creator_name")
    post_album(client)

    response = utils.get_my_albums(client, "another_creator_id")

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_post_empty_album(client, custom_requests_mock):
    post_user(client, "album_creator_id")
    response_post = post_album(client, unwrap_id=False)
    assert response_post.status_code == 200
    album_id = response_post.json()["id"]

    album = utils.get_album(client, album_id, unwrap=True)

    assert str(album["id"]) == str(response_post.json()["id"])
    assert album["name"] == "album_name"
    assert album["description"] == "album_desc"
    assert album["genre"] == "album_genre"
    assert album["songs"] == []


def test_post_album_of_invalid_user_should_fail(client, custom_requests_mock):
    response = post_album(client, "invalid_creator_id", unwrap_id=False)
    assert response.status_code == 404


def test_post_album_with_song(client, custom_requests_mock):
    post_user(client, "album_creator_id")
    song_id = post_song(client)

    response_post = post_album(client, songs_ids=[song_id], unwrap_id=False)
    assert response_post.status_code == 200
    album_id = response_post.json()["id"]

    album = utils.get_album(client, album_id, unwrap=True)

    assert album["songs"][0]["name"] == "song_name"
    assert len(album["songs"]) == 1
    assert album["cover"].startswith("https://example.com")


def test_post_album_associates_song_to_such_album(client, custom_requests_mock):
    post_user(client, "album_creator_id")
    song_id = post_song(client, "album_creator_id")
    album_id = post_album(client, name="album_name", songs_ids=[song_id])

    song = utils.get_song(client, song_id, unwrap=True)

    assert song["album"]["id"] == album_id
    assert song["album"]["name"] == "album_name"


def test_post_album_with_songs_of_other_creator_should_fail(
    client, custom_requests_mock
):
    utils.post_users(client, "album_creator_id", "song_creator_id")
    song_id = post_song(client, uid="song_creator_id")
    response_post_album = post_album(
        client, songs_ids=[song_id], uid="album_creator_id", unwrap_id=False
    )

    assert response_post_album.status_code == 403


def test_put_album(client, custom_requests_mock):
    post_user(client, "album_creator_id")
    album_id = post_album(client)

    response_put = utils.put(
        client, f"/albums/{album_id}", {"name": "updated_test_album"}
    )

    assert response_put.status_code == 200

    album = utils.get_album(client, album_id, unwrap=True)

    assert str(album["id"]) == str(album_id)
    assert album["name"] == "updated_test_album"
    assert album["description"] == "album_desc"


def test_update_songs_in_album_with_songs_of_another_user_should_fail(
    client, custom_requests_mock
):
    utils.post_users(client, "foo_id", "bar_id")

    bar_song_id = post_song(client, uid="bar_id")

    album_id = post_album(client, uid="foo_id")

    response_put = utils.put_album(
        client, album_id, {"songs_ids": f'["{bar_song_id}"]'}, "foo_id"
    )

    assert response_put.status_code == 403


def test_update_songs_in_album(client, custom_requests_mock):
    post_user(client, "album_creator_id")
    song_id = post_song(client, uid="album_creator_id")
    album_id = post_album(client, songs_ids=[song_id])

    response_put = utils.put_album(
        client, album_id, {"songs_ids": "[]"}, "album_creator_id"
    )

    assert response_put.status_code == 200

    response_get = utils.get_album(client, album_id)
    album = response_get.json()

    assert response_get.status_code == 200
    assert len(album["songs"]) == 0


def test_cannot_put_album_of_another_user(client, custom_requests_mock):
    utils.post_users(client, "album_creator_id", "another_creator_id")
    album_id = post_album(client)

    response_put = utils.put_album(
        client, album_id, {"name": "updated_test_album"}, "another_creator_id"
    )

    assert response_put.status_code == 403


def test_delete_album(client, custom_requests_mock):
    post_user(client, "album_creator_id")
    album_id = post_album(client)

    response_delete = utils.delete_album(client, album_id)

    assert response_delete.status_code == 200

    response_get = utils.get_album(client, album_id)

    assert response_get.status_code == 404


def test_cannot_delete_album_of_another_user(client, custom_requests_mock):
    utils.post_users(client, "album_creator_id", "another_creator_id")

    album_id = post_album(client)

    response_delete = utils.delete_album(client, album_id, "another_creator_id")

    assert response_delete.status_code == 403


def test_cannot_delete_album_that_does_not_exist(client, custom_requests_mock):
    post_user(client, "album_creator_id")

    response_delete = utils.delete_album(client, 1)

    assert response_delete.status_code == 404


def test_delete_album_should_not_delete_songs(client, custom_requests_mock):
    post_user(client, "album_creator_id")
    song_id = post_song(client, uid="album_creator_id")
    album_id = post_album(client, songs_ids=[song_id])

    utils.delete_album(client, album_id)

    response_get = utils.get_song(client, song_id)
    song = response_get.json()

    assert response_get.status_code == 200
    assert song["album"] is None


def test_update_cover_updates_cover_timestamp(client, custom_requests_mock):
    post_user(client, "album_creator_id")
    album_id = post_album(client)

    response_get_1 = utils.get_album(client, album_id)

    time.sleep(1)
    with open("./new_cover.img", "wb") as f:
        f.write(b"cover info")
    with open("./new_cover.img", "rb") as f:
        response_put = client.put(
            f"{API_VERSION_PREFIX}/albums/{album_id}",
            files={"cover": ("new_cover.img", f, "plain/text")},
            headers={"uid": "album_creator_id", "api_key": "key"},
        )
        assert response_put.status_code == 200

    response_get_2 = utils.get_album(client, album_id)

    url_1 = response_get_1.json()["cover"]
    url_2 = response_get_2.json()["cover"]

    timestamp_1 = parse_qs(urlparse(url_1).query)["t"][0]
    timestamp_2 = parse_qs(urlparse(url_2).query)["t"][0]

    assert timestamp_1 != timestamp_2


def test_add_song_to_album(client, custom_requests_mock):
    post_user(client, "album_creator_id")
    song_id_1 = post_song(client, uid="album_creator_id", name="song1")
    song_id_2 = post_song(client, uid="album_creator_id", name="song2")

    album_id = post_album(client, uid="album_creator_id", songs_ids=[song_id_1])

    response_put = utils.put_album(
        client,
        album_id,
        {"songs_ids": f"[{song_id_1}, {song_id_2}]"},
        "album_creator_id",
    )

    assert response_put.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"api_key": "key", "uid": "album_creator_id"},
    )

    album = response_get.json()
    assert response_get.status_code == 200
    assert len(album["songs"]) == 2


def test_listener_cannot_post_album(client, custom_requests_mock):
    post_user(client, "listener_id", "listener_name")

    response_post = post_album(
        client, role="listener", uid="listener_id", unwrap_id=False
    )
    assert response_post.status_code == 403


def test_admin_can_delete_album_of_another_user(client, custom_requests_mock):
    utils.post_users(client, "album_creator_id", "admin_id")

    album_id = post_album(client, uid="album_creator_id")

    response_delete = utils.delete_album(client, album_id, "admin_id", role="admin")

    assert response_delete.status_code == 200


def test_admin_can_edit_album_of_another_user(client, custom_requests_mock):
    utils.post_users(client, "album_creator_id", "admin_id")

    album_id = post_album(client, uid="album_creator_id")

    response_put = utils.put_album(
        client, album_id, {"name": "new_name"}, "admin_id", role="admin"
    )

    assert response_put.status_code == 200
