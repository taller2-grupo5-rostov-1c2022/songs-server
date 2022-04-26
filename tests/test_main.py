import os

os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_unauthorized_get():
    response = client.get("/api/v1/songs/")
    assert response.status_code == 403


def test_get_songs():
    response = client.get("/api/v1/songs/", headers={"api_key": "key"})
    assert response.status_code == 200


def test_post_song():
    response_post = client.post(
        "/api/v1/songs/",
        json={
            "info": {"name": "song123", "artist_name": "artist123"},
            "file": "file123",
        },
        headers={"api_key": "key"},
    )
    assert response_post.status_code == 200
    response_get = client.get(
        "/api/v1/songs/" + str(response_post.json()["id"]), headers={"api_key": "key"}
    )
    assert response_get.status_code == 200
    assert response_get.json()["name"] == "song123"


################################################################################


def test_get_songs2():
    response = client.get("/api/v1/songs/", headers={"api_key": "key"})
    assert response.status_code == 200


def test_post_song2():
    with open("./tests/test.song", "wb") as f:
        f.write(b"test")
    with open("./tests/test.song", "rb") as f:
        response_post = client.post(
            "/api/v2/songs/",
            params={
                "name": "test_song",
                "description": "test_description",
                "creator": "test_creator",
                "artists": "test_artists",
            },
            files={"file": ("song.txt", f, "plain/text")},
            headers={"api_key": "key"},
        )
    assert response_post.status_code == 200
    response_get = client.get(
        "/api/v2/songs/" + str(response_post.json()["id"]),
        headers={"api_key": "key"},
    )
    assert response_get.json()["id"] == response_post.json()["id"]
    assert response_get.json()["name"] == "test_song"
    assert response_get.json()["description"] == "test_description"
    assert response_get.json()["creator"] == "test_creator"
    assert response_get.json()["artists"] == "test_artists"


def test_put_song2():
    with open("./tests/test.song", "wb") as f:
        f.write(b"test")
    with open("./tests/test.song", "rb") as f:
        response_post = client.post(
            "/api/v2/songs/",
            params={
                "name": "up_test_song",
                "description": "up_test_description",
                "creator": "up_test_creator",
                "artists": "up_test_artists",
            },
            files={"file": ("song.txt", f, "plain/text")},
            headers={"api_key": "key"},
        )
    assert response_post.status_code == 200

    response_update = client.put(
        "/api/v2/songs/",
        params={
            "song_id": response_post.json()["id"],
            "name": "updated_test_song",
            "artists": "updated_test_artists",
        },
        headers={"api_key": "key"},
    )
    assert response_update.status_code == 200
    assert response_update.json()["id"] == response_post.json()["id"]

    response_get = client.get(
        "/api/v2/songs/" + str(response_post.json()["id"]),
        headers={"api_key": "key"},
    )

    assert response_get.json()["id"] == response_post.json()["id"]
    assert response_get.json()["name"] == "updated_test_song"
    assert response_get.json()["description"] == "up_test_description"
    assert response_get.json()["creator"] == "up_test_creator"
    assert response_get.json()["artists"] == "updated_test_artists"
