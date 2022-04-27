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


def post_song2(
    name: str,
    description: str,
    creator: str,
    artists: str,
    file: str,
    headers: dict,
):
    with open(file, "wb") as f:
        f.write(b"test")
    with open(file, "rb") as f:
        response_post = client.post(
            "/api/v2/songs/",
            data={
                "name": name,
                "description": description,
                "creator": creator,
                "artists": artists,
            },
            files={"file": ("song.txt", f, "plain/text")},
            headers=headers,
        )
    return response_post


def test_get_songs2():
    response = client.get("/api/v1/songs/", headers={"api_key": "key"})
    assert response.status_code == 200


def test_post_song2():
    response_post = post_song2(
        "post_test_song",
        "post_test_description",
        "post_test_creator",
        "post_test_artists",
        "./tests/test.song",
        {"api_key": "key"},
    )
    assert response_post.status_code == 200
    response_get = client.get(
        "/api/v2/songs/" + str(response_post.json()["id"]),
        headers={"api_key": "key"},
    )
    assert response_get.json()["id"] == response_post.json()["id"]
    assert response_get.json()["name"] == "post_test_song"
    assert response_get.json()["description"] == "post_test_description"
    assert response_get.json()["creator"] == "post_test_creator"
    assert response_get.json()["artists"] == "post_test_artists"


def test_put_song2():
    response_post = post_song2(
        "put_test_song",
        "put_test_description",
        "put_test_creator",
        "put_test_artists",
        "./tests/test.song",
        {"api_key": "key"},
    )
    assert response_post.status_code == 200

    response_update = client.put(
        "/api/v2/songs/" + str(response_post.json()["id"]),
        data={
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
    assert response_get.json()["description"] == "put_test_description"
    assert response_get.json()["creator"] == "put_test_creator"
    assert response_get.json()["artists"] == "updated_test_artists"


def test_get_song_by_creator2():

    for i in range(3):
        response_post = post_song2(
            "byCreator_test_song" + str(i),
            "byCreator_test_description",
            "byCreator_test_creator",
            "byCreator_test_artists",
            "./tests/test.song",
            {"api_key": "key"},
        )
        assert response_post.status_code == 200
    for i in range(3):
        response_post = post_song2(
            "notByCreator_test_song" + str(i),
            "notByCreator_test_description",
            "notByCreator_test_creator",
            "notByCreator_test_artists",
            "./tests/test.song",
            {"api_key": "key"},
        )
        assert response_post.status_code == 200

    response_get = client.get(
        "/api/v2/songs/?creator=byCreator_test_creator",
        headers={"api_key": "key"},
    )

    assert len(response_get.json()) >= 3  # local runs may use a dirty db
    for song in response_get.json():
        assert song["creator"] == "byCreator_test_creator"
