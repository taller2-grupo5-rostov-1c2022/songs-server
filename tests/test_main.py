from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_songs():
    response = client.get("/api/v1/songs/")
    assert response.status_code == 200

def test_post_song():
    response_post = client.post("/api/v1/songs/", json={"name": "song123"})
    assert response_post.status_code == 200
    response_get = client.get("/api/v1/songs/" + str(response_post.json()["id"]))
    assert response_get.status_code == 200
    assert response_get.json()["name"] == "song123"