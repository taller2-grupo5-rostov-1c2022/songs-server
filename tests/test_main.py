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
        "/api/v1/songs/", json={"name": "song123"}, headers={"api_key": "key"}
    )
    assert response_post.status_code == 200
    response_get = client.get(
        "/api/v1/songs/" + str(response_post.json()["id"]), headers={"api_key": "key"}
    )
    assert response_get.status_code == 200
    assert response_get.json()["name"] == "song123"
