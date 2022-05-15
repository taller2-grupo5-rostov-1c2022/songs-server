from tests.utils import (
    API_VERSION_PREFIX,
    post_user,
    post_song,
    post_album,
)


def test_unauthorized_get(client):
    response = client.get(f"{API_VERSION_PREFIX}/users/")
    assert response.status_code == 403


def test_get_users(client):
    response = client.get(f"{API_VERSION_PREFIX}/users/", headers={"api_key": "key"})
    assert response.status_code == 200


def test_get_user_that_was_not_created(client):
    response = client.get(
        f"{API_VERSION_PREFIX}/users/not_created_user", headers={"api_key": "key"}
    )

    assert response.status_code == 404


def test_get_my_users(client):
    post_user(client, "user_id", "user_name")

    response = client.get(
        f"{API_VERSION_PREFIX}/users/user_id",
        headers={"api_key": "key", "uid": "user_id"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "user_name"


def test_get_my_user_with_invalid_uid_should_fail(client):
    response = client.get(
        f"{API_VERSION_PREFIX}/my_users/",
        headers={"api_key": "key", "uid": "not_created_id"},
    )

    assert response.status_code == 404


def test_post_user(client):
    response_post = post_user(
        client,
        "new_user_id",
        "user_name",
        interests="my_interests",
        location="Buenos Aires",
    )
    assert response_post.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/users/new_user_id", headers={"api_key": "key"}
    )

    assert response_get.status_code == 200
    assert response_get.json()["id"] == "new_user_id"
    assert response_get.json()["interests"] == "my_interests"
    assert response_get.json()["location"] == "Buenos Aires"


def test_user_songs_are_updated_after_posting_song(client):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id")

    response = client.get(
        f"{API_VERSION_PREFIX}/users/user_id", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()["songs"]) == 1
    assert response.json()["songs"][0]["name"] == "song_name"


def test_user_albums_are_updated_after_posting_album(client):
    post_user(client, "user_id", "user_name")
    post_album(client, uid="user_id")

    response = client.get(
        f"{API_VERSION_PREFIX}/users/user_id", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()["albums"]) == 1
    assert response.json()["albums"][0]["name"] == "album_name"


def test_put_user(client):
    post_user(client, "user_id", "user_name")

    response_put = client.put(
        f"{API_VERSION_PREFIX}/users/user_id",
        data={"interests": "nothing", "location": "Argentina"},
        headers={"api_key": "key", "uid": "user_id"},
    )

    assert response_put.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/users/user_id", headers={"api_key": "key"}
    )

    assert response_get.status_code == 200
    assert response_get.json()["interests"] == "nothing"
    assert response_get.json()["location"] == "Argentina"
    assert response_get.json()["name"] == "user_name"


def test_cannot_update_info_of_another_user(client):
    post_user(client, "user_id", "user_name")
    post_user(client, "another_user_id", "user_name")

    response = client.put(
        f"{API_VERSION_PREFIX}/users/user_id",
        data={"interests": "nothing", "location": "Argentina"},
        headers={"api_key": "key", "uid": "another_user_id"},
    )

    assert response.status_code == 403


def test_delete_user(client):
    post_user(client, "user_id", "user_name")

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/users/user_id",
        headers={"api_key": "key", "uid": "user_id"},
    )

    assert response_delete.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/users/user_id", headers={"api_key": "key"}
    )

    assert response_get.status_code == 404


def test_cannot_delete_another_user(client):
    post_user(client, "user_id", "user_name")
    post_user(client, "another_user_id", "user_name")

    response = client.delete(
        f"{API_VERSION_PREFIX}/users/user_id",
        headers={"api_key": "key", "uid": "another_user_id"},
    )

    assert response.status_code == 403


def test_update_pfp_updates_pfp_timestamp(client):
    post_user(client, "user_id", "user_name")
    response_get_1 = client.get(
        f"{API_VERSION_PREFIX}/users/user_id", headers={"api_key": "key"}
    )

    with open("./new_pfp.img", "wb") as f:
        f.write(b"pfp data")
    with open("./new_pfp.img", "rb") as f:
        response_put = client.put(
            f"{API_VERSION_PREFIX}/users/user_id",
            files={"img": ("new_pfp.img", f, "plain/text")},
            headers={"uid": "user_id", "api_key": "key"},
        )
        assert response_put.status_code == 200

    response_get_2 = client.get(
        f"{API_VERSION_PREFIX}/users/user_id", headers={"api_key": "key"}
    )

    assert (
        response_get_1.json()["pfp_last_update"]
        < response_get_2.json()["pfp_last_update"]
    )
