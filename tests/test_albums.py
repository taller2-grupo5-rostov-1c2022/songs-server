from tests.utils import post_user, post_song, post_album
from tests.utils import API_VERSION_PREFIX
import time


def test_unauthorized_get(client):
    response = client.get(API_VERSION_PREFIX + "/albums/")
    assert response.status_code == 403


def test_get_albums(client):
    response = client.get(API_VERSION_PREFIX + "/albums/", headers={"api_key": "key"})
    assert response.status_code == 200


def test_get_album_by_invalid_id(client):
    response = client.get(API_VERSION_PREFIX + "/albums/5", headers={"api_key": "key"})

    assert response.status_code == 404


def test_get_album_of_user_without_albums(client):
    post_user(client, "album_creator_id", "album_creator_name")
    response = client.get(
        API_VERSION_PREFIX + "/my_albums/",
        headers={"uid": "album_creator_id", "api_key": "key"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_my_albums(client):
    post_user(client, "album_creator_id", "album_creator_name")

    post_album(client)

    response = client.get(
        API_VERSION_PREFIX + "/my_albums/",
        headers={"uid": "album_creator_id", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "album_name"
    assert response.json()[0]["description"] == "album_desc"
    assert response.json()[0]["genre"] == "album_genre"
    assert response.json()[0]["songs"] == []
    assert len(response.json()) == 1


def test_get_my_albums_does_not_return_albums_of_other_users(client):
    post_user(client, "album_creator_id", "album_creator_name")
    post_user(client, "another_creator_id", "another_creator_name")
    post_album(client)

    response = client.get(
        API_VERSION_PREFIX + "/my_albums/",
        headers={"uid": "another_creator_id", "api_key": "key"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_post_empty_album(client):
    post_user(client, "album_creator_id", "album_creator_name")
    response_post = post_album(client)
    assert response_post.status_code == 200

    response_get = client.get(
        API_VERSION_PREFIX + "/albums/" + str(response_post.json()["id"]),
        headers={"api_key": "key"},
    )

    assert str(response_get.json()["id"]) == str(response_post.json()["id"])
    assert response_get.json()["name"] == "album_name"
    assert response_get.json()["description"] == "album_desc"
    assert response_get.json()["genre"] == "album_genre"
    assert response_get.json()["songs"] == []


def test_post_album_of_invalid_user_should_fail(client):
    response = post_album(client, "invalid_creator_id")
    assert response.status_code == 404


def test_post_album_with_song(client):
    post_user(client, "album_creator_id", "album_creator_name")
    response_post_song = post_song(client, "album_creator_id")

    response_post_album = post_album(
        client, songs_ids=[response_post_song.json()["id"]]
    )
    assert response_post_album.status_code == 200

    response_get = client.get(
        API_VERSION_PREFIX + "/albums/" + str(response_post_album.json()["id"]),
        headers={"api_key": "key"},
    )
    assert response_get.json()["songs"][0]["name"] == "song_name"
    assert len(response_get.json()["songs"]) == 1
    assert response_get.json()["cover"] == "https://example.com"
    assert response_get.json()["sub_level"] == 1


def test_post_album_associates_song_to_such_album(client):
    post_user(client, "album_creator_id", "album_creator_name")
    response_post_song = post_song(client, "album_creator_id")
    response_post_album = post_album(
        client, songs_ids=[response_post_song.json()["id"]]
    )
    response_get_song = client.get(
        API_VERSION_PREFIX + "/songs/" + str(response_post_song.json()["id"]),
        headers={"api_key": "key"},
    )
    print(response_get_song.json())
    assert response_get_song.json()["album"]["id"] == response_post_album.json()["id"]
    assert response_get_song.json()["album"]["name"] == "album_name"


def test_post_album_with_songs_of_other_creator_should_fail(client):
    post_user(client, "album_creator_id", "album_creator_name")
    post_user(client, "song_creator_id", "song_creator_name")
    response_post_song = post_song(client)
    response_post_album = post_album(
        client, songs_ids=[response_post_song.json()["id"]]
    )
    assert response_post_album.status_code == 403


def test_put_album(client):
    post_user(client, "album_creator_id", "album_creator_name")
    response_post = post_album(client)
    assert response_post.status_code == 200

    response_update = client.put(
        API_VERSION_PREFIX + "/albums/" + str(response_post.json()["id"]),
        data={"name": "updated_test_album", "sub_level": 5},
        headers={"api_key": "key", "uid": "album_creator_id"},
    )
    assert response_update.status_code == 200

    response_get = client.get(
        API_VERSION_PREFIX + "/albums/" + str(response_post.json()["id"]),
        headers={"api_key": "key"},
    )

    assert str(response_get.json()["id"]) == str(response_post.json()["id"])
    assert response_get.json()["name"] == "updated_test_album"
    assert response_get.json()["sub_level"] == 5
    assert response_get.json()["description"] == "album_desc"


def test_update_songs_in_album_with_songs_of_another_user_should_fail(client):
    post_user(client, "foo_id", "foo_name")
    post_user(client, "bar_id", "bar_name")

    bar_song_id = post_song(client, uid="bar_id").json()["id"]

    response_post_album = post_album(client, uid="foo_id")
    assert response_post_album.status_code == 200

    response_update_album = client.put(
        f"{API_VERSION_PREFIX}/albums/{response_post_album.json()['id']}",
        headers={"api_key": "key", "uid": "foo_id"},
        data={"songs_ids": f'["{bar_song_id}"]'},
    )
    assert response_update_album.status_code == 403


def test_update_songs_in_album(client):
    post_user(client, "album_creator_id", "album_creator_name")
    response_post_song = post_song(client, uid="album_creator_id")
    response_post_album = post_album(client, songs_ids=response_post_song.json()["id"])

    response_update = client.put(
        API_VERSION_PREFIX + "/albums/" + str(response_post_album.json()["id"]),
        data={"songs_ids": "[]"},
        headers={"api_key": "key", "uid": "album_creator_id"},
    )
    assert response_update.status_code == 200

    response_get = client.get(
        API_VERSION_PREFIX + "/albums/" + str(response_post_album.json()["id"]),
        headers={"api_key": "key"},
    )
    assert response_get.status_code == 200
    assert len(response_get.json()["songs"]) == 0


def test_cannot_put_album_of_another_user(client):
    post_user(client, "album_creator_id", "album_creator_name")
    response_post = post_album(client)
    assert response_post.status_code == 200

    response_update = client.put(
        API_VERSION_PREFIX + "/albums/" + str(response_post.json()["id"]),
        data={"name": "updated_test_album"},
        headers={"api_key": "key", "uid": "another_creator_id"},
    )
    assert response_update.status_code == 403


def test_delete_album(client):
    post_user(client, "album_creator_id", "album_creator_name")
    response_post = post_album(client)

    response_delete = client.delete(
        API_VERSION_PREFIX
        + "/albums/"
        + str(response_post.json()["id"])
        + "?uid=album_creator_id",
        headers={"api_key": "key"},
    )
    assert response_delete.status_code == 200

    response_get = client.get(
        API_VERSION_PREFIX + "/albums/" + str(response_post.json()["id"]),
        headers={"api_key": "key"},
    )
    print(response_get.json())
    assert response_get.status_code == 404


def test_cannot_delete_album_of_another_user(client):
    post_user(client, "album_creator_id", "album_creator_name")
    post_user(client, "another_creator_id", "another_creator_name")

    response_post = post_album(client)

    response_delete = client.delete(
        API_VERSION_PREFIX
        + "/albums/"
        + str(response_post.json()["id"])
        + "?uid=another_creator_id",
        headers={"api_key": "key"},
    )
    assert response_delete.status_code == 403


def test_cannot_delete_album_that_does_not_exist(client):
    post_user(client, "album_creator_id", "album_creator_name")

    response_delete = client.delete(
        API_VERSION_PREFIX + "/albums/1?uid=another_creator_id",
        headers={"api_key": "key"},
    )

    assert response_delete.status_code == 404


def test_delete_album_should_not_delete_songs(client):
    post_user(client, "album_creator_id", "album_creator_name")
    response_post_song = post_song(client, uid="album_creator_id")
    response_post = post_album(client, songs_ids=[response_post_song.json()["id"]])
    response_delete = client.delete(
        API_VERSION_PREFIX
        + "/albums/"
        + str(response_post.json()["id"])
        + "?uid=album_creator_id",
        headers={"api_key": "key"},
    )
    assert response_delete.status_code == 200

    response_get = client.get(
        API_VERSION_PREFIX + "/songs/" + str(response_post_song.json()["id"]),
        headers={"api_key": "key"},
    )

    assert response_get.status_code == 200
    assert response_get.json()["album"] is None


def test_update_cover_updates_cover_timestamp(client):
    post_user(client, "album_creator_id", "album_creator_name")
    album_id = post_album(client).json()["id"]

    response_get_1 = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"api_key": "key"},
    )

    with open("./new_cover.img", "wb") as f:
        f.write(b"cover info")
    with open("./new_cover.img", "rb") as f:
        response_put = client.put(
            f"{API_VERSION_PREFIX}/albums/{album_id}",
            files={"cover": ("new_cover.img", f, "plain/text")},
            headers={"uid": "album_creator_id", "api_key": "key"},
        )
        assert response_put.status_code == 200

    response_get_2 = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"api_key": "key"},
    )

    assert (
        response_get_1.json()["cover_last_update"]
        < response_get_2.json()["cover_last_update"]
    )
