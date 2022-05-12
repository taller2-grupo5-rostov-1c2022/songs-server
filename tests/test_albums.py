from tests.utils import post_user, post_song, post_album
from tests.utils import API_VERSION_PREFIX


def test_unauthorized_get(client):
    response = client.get(API_VERSION_PREFIX + "/albums/")
    assert response.status_code == 403


def test_get_albums(client):
    response = client.get(API_VERSION_PREFIX + "/albums/", headers={"api_key": "key"})
    assert response.status_code == 200


def test_get_album_of_user_without_albums(client):
    post_user(client, "album_creator_id", "album_creator_name")
    response = client.get(
        API_VERSION_PREFIX + "/my_albums/",
        headers={"uid": "album_creator_id", "api_key": "key"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_album_of_invalid_user(client):
    response = client.get(
        API_VERSION_PREFIX + "/my_albums/",
        headers={"uid": "album_creator_id", "api_key": "key"},
    )
    assert response.status_code == 404


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
        data={"uid": "album_creator_id", "name": "updated_test_album", "sub_level": 5},
        headers={"api_key": "key"},
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


def test_update_songs_in_album(client):
    post_user(client, "album_creator_id", "album_creator_name")
    response_post_song = post_song(client, uid="album_creator_id")
    response_post_album = post_album(client, songs_ids=response_post_song.json()["id"])

    response_update = client.put(
        API_VERSION_PREFIX + "/albums/" + str(response_post_album.json()["id"]),
        data={"uid": "album_creator_id", "songs_ids": "[]"},
        headers={"api_key": "key"},
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
        data={"uid": "another_creator_id", "name": "updated_test_album"},
        headers={"api_key": "key"},
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
    client.delete(
        API_VERSION_PREFIX
        + "/albums/"
        + str(response_post.json()["id"])
        + "?uid=another_creator_id",
        headers={"api_key": "key"},
    )

    response_get = client.get(
        API_VERSION_PREFIX + "/songs/" + str(response_post_song.json()["id"]),
        headers={"api_key": "key"},
    )

    assert response_get.status_code == 200
    assert response_get.json()["album_info"] is None
