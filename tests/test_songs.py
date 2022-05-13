from tests.utils import post_song, post_user
from tests.utils import API_VERSION_PREFIX


def test_unauthorized_get(client):
    response = client.get(API_VERSION_PREFIX + "/songs/")
    assert response.status_code == 403


def test_get_songs(client):
    response = client.get(API_VERSION_PREFIX + "/songs/", headers={"api_key": "key"})
    assert response.status_code == 200


def test_post_song(client):
    post_user(client, "song_creator_id", "song_creator")
    response_post = post_song(client)
    assert response_post.status_code == 200
    response_get = client.get(
        API_VERSION_PREFIX + "/songs/" + str(response_post.json()["id"]),
        headers={"api_key": "key"},
    )
    assert str(response_get.json()["id"]) == str(response_post.json()["id"])
    assert response_get.json()["name"] == "song_name"
    assert response_get.json()["description"] == "song_desc"
    assert response_get.json()["artists"] == [{"name": "song_artist_name"}]
    assert response_get.json()["genre"] == "song_genre"
    assert response_get.json()["file"] == "https://example.com"
    assert response_get.json()["album"] is None


def test_cannot_post_song_with_not_created_user(client):
    response_post = post_song(client)
    assert response_post.status_code == 403


def test_put_song(client):
    post_user(client, "song_creator_id", "song_creator")
    response_post = post_song(client)
    assert response_post.status_code == 200

    response_update = client.put(
        API_VERSION_PREFIX + "/songs/" + str(response_post.json()["id"]),
        data={
            "name": "updated_test_song",
            "artists": '["updated_test_artists"]',
        },
        headers={
            "api_key": "key",
            "uid": "song_creator_id",
        },
    )
    assert response_update.status_code == 200
    assert response_update.json()["id"] == response_post.json()["id"]

    response_get = client.get(
        API_VERSION_PREFIX + "/songs/" + str(response_post.json()["id"]),
        headers={"api_key": "key"},
    )

    assert str(response_get.json()["id"]) == str(response_post.json()["id"])
    assert response_get.json()["name"] == "updated_test_song"
    assert response_get.json()["description"] == "song_desc"
    assert response_get.json()["artists"] == [{"name": "updated_test_artists"}]


def test_cannot_put_song_of_another_user(client):
    post_user(client, "song_creator_id", "song_creator")
    post_user(client, "another_creator_id", "another_creator_name")
    response_post = post_song(client)

    response_update = client.put(
        API_VERSION_PREFIX + "/songs/" + str(response_post.json()["id"]),
        data={
            "name": "updated_test_song",
        },
        headers={
            "api_key": "key",
            "uid": "another_creator_id",
        },
    )
    assert response_update.status_code == 403


def test_get_song_by_creator(client):
    post_user(client, "byCreator_test_user_id", "byCreator_test_user_name")
    post_user(client, "notByCreator_test_user_id", "notByCreator_test_user_name")

    for i in range(3):
        response_post = post_song(
            client, "byCreator_test_user_id", "byCreator_test_song" + str(i)
        )
        assert response_post.status_code == 200

    for i in range(3):
        response_post = post_song(
            client, "notByCreator_test_user_id", "notByCreator_test_song" + str(i)
        )
        assert response_post.status_code == 200

    response_get = client.get(
        API_VERSION_PREFIX + "/songs/?creator=byCreator_test_user_id",
        headers={"api_key": "key"},
    )
    assert len(response_get.json()) == 3
    for i, song in enumerate(response_get.json()):
        assert song["name"] == "byCreator_test_song" + str(i)


def test_delete_song(client):
    post_user(client, "song_creator_id", "song_creator")
    response_post = post_song(client)
    assert response_post.status_code == 200

    response_delete = client.delete(
        API_VERSION_PREFIX + f"/songs/{str(response_post.json()['id'])}",
        headers={
            "api_key": "key",
            "uid": "song_creator_id",
        },
    )

    assert response_delete.status_code == 200

    response_get = client.get(
        API_VERSION_PREFIX + "/songs/" + str(response_post.json()["id"]),
        headers={"api_key": "key"},
    )

    assert response_get.status_code == 404


def test_cannot_delete_song_of_another_user(client):
    post_user(client, "song_creator_id", "song_creator")
    post_user(client, "another_creator_id", "another_creator_name")
    response_post = post_song(client)
    response_delete = client.delete(
        API_VERSION_PREFIX + f"/songs/{str(response_post.json()['id'])}",
        headers={"api_key": "key", "uid": "another_creator_id"},
    )

    assert response_delete.status_code == 403


def test_cannot_delete_song_that_does_not_exist(client):
    post_user(client, "song_creator_id", "song_creator")
    response_delete = client.delete(
        API_VERSION_PREFIX + "/songs/1",
        headers={"api_key": "key", "uid": "another_creator_id"},
    )

    assert response_delete.status_code == 404


def test_get_my_songs_should_retrieve_two_songs(client):
    post_user(client, "song_creator_id", "song_creator")
    post_song(client, uid="song_creator_id", name="happy_song")
    post_song(client, uid="song_creator_id", name="sad_song")

    response_get = client.get(
        API_VERSION_PREFIX + "/my_songs/",
        headers={"api_key": "key", "uid": "song_creator_id"},
    )

    body_songs = response_get.json()

    assert response_get.status_code == 200
    assert len(body_songs) == 2
    assert body_songs[0]["name"] == "happy_song"
    assert body_songs[0]["artists"] == [{"name": "song_artist_name"}]
    assert body_songs[1]["name"] == "sad_song"


def test_post_with_invalid_artists_format_should_fail(client):
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
            headers={"uid": "song_creator_id", "api_key": "key"},
        )

    assert response_post.status_code == 422
