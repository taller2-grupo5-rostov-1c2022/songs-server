from tests.utils import create_user, post_song, post_album
from tests.utils import API_VERSION_PREFIX


def test_unauthorized_get(client):
    response = client.get(API_VERSION_PREFIX + "/albums/")
    assert response.status_code == 403


def test_get_albums(client):
    response = client.get(API_VERSION_PREFIX + "/albums/", headers={"api_key": "key"})
    assert response.status_code == 200


def test_post_empty_album(client):
    create_user(client, "album_creator_id", "album_creator_name")
    response_post = post_album(client)
    assert response_post.status_code == 200

    response_get = client.get(
        API_VERSION_PREFIX + "/albums/" + str(response_post.json()["id"]),
        headers={"api_key": "key"},
    )

    print(response_get.json())

    assert str(response_get.json()["id"]) == str(response_post.json()["id"])
    assert response_get.json()["name"] == "album_name"
    assert response_get.json()["description"] == "album_desc"
    assert response_get.json()["genre"] == "album_genre"
    assert response_get.json()["artists"] == [
        {"artist_name": "artist_name_1"},
        {"artist_name": "artist_name_2"},
    ]
    assert response_get.json()["songs"] == []


def test_post_album_with_song(client):
    create_user(client, "album_creator_id", "album_creator_name")
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


def test_put_album(client):
    create_user(client, "album_creator_id", "album_creator_name")
    response_post = post_album(client)
    assert response_post.status_code == 200

    response_update = client.put(
        API_VERSION_PREFIX + "/albums/" + str(response_post.json()["id"]),
        data={"user_id": "album_creator_id", "name": "updated_test_album"},
        headers={"api_key": "key"},
    )
    assert response_update.status_code == 200

    response_get = client.get(
        API_VERSION_PREFIX + "/albums/" + str(response_post.json()["id"]),
        headers={"api_key": "key"},
    )

    assert str(response_get.json()["id"]) == str(response_post.json()["id"])
    assert response_get.json()["name"] == "updated_test_album"
    assert response_get.json()["description"] == "album_desc"


def test_cannot_put_album_of_another_user(client):
    create_user(client, "album_creator_id", "album_creator_name")
    response_post = post_album(client)
    assert response_post.status_code == 200

    response_update = client.put(
        API_VERSION_PREFIX + "/albums/" + str(response_post.json()["id"]),
        data={"user_id": "another_creator_id", "name": "updated_test_album"},
        headers={"api_key": "key"},
    )
    assert response_update.status_code == 403


def test_delete_album(client):
    create_user(client, "album_creator_id", "album_creator_name")
    response_post = post_album(client)

    response_delete = client.delete(
        API_VERSION_PREFIX + "/albums/" + str(response_post.json()["id"]) + "?user_id=album_creator_id",
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
    create_user(client, "album_creator_id", "album_creator_name")
    create_user(client, "another_creator_id", "another_creator_name")

    response_post = post_album(client)

    response_delete = client.delete(
        API_VERSION_PREFIX + "/albums/" + str(response_post.json()["id"]) + "?user_id=another_creator_id",
        headers={"api_key": "key"},
    )
    assert response_delete.status_code == 403


def test_cannot_delete_album_that_does_not_exist(client):
    create_user(client, "album_creator_id", "album_creator_name")

    response_delete = client.delete(
        API_VERSION_PREFIX + "/albums/1?user_id=another_creator_id",
        headers={"api_key": "key"},
    )

    assert response_delete.status_code == 404


def test_delete_album_should_not_delete_songs(client):
    create_user(client, "album_creator_id", "album_creator_name")
    response_post_song = post_song(client, user_id="album_creator_id")
    response_post = post_album(client, songs_ids = [response_post_song.json()["id"]])
    client.delete(
        API_VERSION_PREFIX + "/albums/" + str(response_post.json()["id"]) + "?user_id=another_creator_id",
        headers={"api_key": "key"},
    )

    response_get = client.get(
        API_VERSION_PREFIX + "/songs/" + str(response_post_song.json()["id"]),
        headers={"api_key": "key"},
    )

    assert response_get.status_code == 200
    assert response_get.json()["album_info"] is None

